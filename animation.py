# %%
import networkx as nx
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch

from network import SCNetwork


def get_data_at_t(data, timestep):
    """
    Get data at the given time step.
    """
    return data[data.timestep == timestep]


def get_order_flow(data):
    # Select the rows in which nodes has incoming orders
    rows_w_order = data[~data["order_from"].isna()]
    order_flow = {}
    for _, row in rows_w_order.iterrows():
        buyer, seller = row["order_from"], row["node_idx"]
        order_flow[(buyer, seller)] = int(row["buy_amount"])
    return order_flow


def get_material_flow(data):
    """
    Material need a timestep to be delivered.
    Material flow has lag of one timestep from seller to buyer.
    The last meterial will arrive at `max_timestep + 1`.
    """
    rows_w_order = data[~data["order_from"].isna()]
    material_flow = {}
    for _, row in rows_w_order.iterrows():
        buyer, seller = row["order_from"], row["node_idx"]
        material_flow[(seller, buyer)] = int(row["receive_amount"])
    return material_flow


def get_cash_flow(data):
    rows_w_order = data[~data["cash_from"].isna()]
    cash_flow = {}
    for _, row in rows_w_order.iterrows():
        sender, receiver = row["cash_from"], row["node_idx"]
        cash_flow[(sender, receiver)] = row["pay_amount"]
    return cash_flow


# Return the list of bankrupt nodes
def get_bankrupt_nodes(data):
    bankrupt_nodes = data.loc[data.is_bankrupt == True, ["node_idx"]]
    return list(bankrupt_nodes["node_idx"])


def update(ts, data, network, ax, max_ts):
    ax.clear()
    ax.set_ymargin(0.2)

    G = network.G.copy()
    layout = network.layout.copy()
    node_colors = network.node_colors.copy()
    node_labels = network.node_labels.copy()

    # Orders being placed at current timestep
    data_at_t = get_data_at_t(data, ts)
    order_flow = get_order_flow(data_at_t)
    # Material ordered at the prev `t` being delivered at current`t`.
    data_at_prev_t = get_data_at_t(data, ts - 1)
    material_flow = get_material_flow(data_at_prev_t)
    cash_flow = get_cash_flow(data_at_t)

    
    if ts == (max_ts + 1): 
        data_at_t = data_at_prev_t
    bankrupt_nodes = get_bankrupt_nodes(data_at_t)
    bankrupt_info = "" if not bankrupt_nodes else f": node(s) {', '.join(map(str, bankrupt_nodes))} bankrupted"
    for node_idx in bankrupt_nodes:
        node_colors[node_idx] = network.config["node_options"]["bankrupt"]["color"]
        ebunch = list(G.in_edges(node_idx)) + list(G.out_edges(node_idx))
        G.remove_edges_from(ebunch)

    
    # Check if the network is connected (failure) or not.
    unconnected_info = ""
    if not nx.has_path(G, network.dummy_raw_material,  network.dummy_market):
        unconnected_info = f"\nNetwork is unconnected, simulation ends at timestep {max_ts}."

    # Styling
    graph_options = network.config["graph_options"]

    order_flow_options = network.config["flow_options"]["order"]
    material_flow_options = network.config["flow_options"]["material"]
    cash_flow_options = network.config["flow_options"]["cash"]

    order_flow_label_options = network.config["flow_label_options"]["order"]
    material_flow_label_options = network.config["flow_label_options"]["material"]
    cash_flow_label_options = network.config["flow_label_options"]["cash"]
   

    # Plotting
    ax.set_title(f"Timestep [{ts}] {bankrupt_info} {unconnected_info}")
    nx.draw_networkx(G, layout, node_color=node_colors, labels=node_labels, **graph_options)

    # Order flows
    nx.draw_networkx_edges(G, layout, edgelist=list(order_flow.keys()), **order_flow_options)
    nx.draw_networkx_edge_labels(G, layout, edge_labels=order_flow, **order_flow_label_options)

    # Material flows
    nx.draw_networkx_edges(G, layout, edgelist=list(material_flow.keys()), **material_flow_options)
    nx.draw_networkx_edge_labels(G, layout, edge_labels=material_flow, **material_flow_label_options)

    nx.draw_networkx_edges(G, layout, edgelist=list(cash_flow.keys()), **cash_flow_options)
    nx.draw_networkx_edge_labels(G, layout, edge_labels=cash_flow, **cash_flow_label_options)

    # Legend
    legend_elements = [
        Line2D((0, 0), (1, 1), 
              label='Order flow', linewidth=3, alpha=0.75,
              color=order_flow_options["edge_color"]),
        Line2D((0, 0), (1, 1),
               label='Material flow', linewidth=3, alpha=0.75,
               color=material_flow_options["edge_color"]),
        Line2D((0, 0), (1, 1),
               label='Cash flow', linewidth=3, alpha=0.75,
               color=cash_flow_options["edge_color"]),
    ]
    ax.legend(handles=legend_elements, 
              loc='lower center', 
              frameon=False,
              ncol=3)


def animate():
    # Data preparation
    data_file = "output_data/output__sim_0.csv"
    data = pd.read_csv(data_file)

    max_ts = data.timestep.max()

    network = SCNetwork(config_file="configs/network_config.yaml")
    fig, ax = network.draw()

    # Remove frames
    for pos in ["top", "left", "bottom", "right"]:
        ax.spines[pos].set_visible(False)

    anim = animation.FuncAnimation(fig,
                                   update,
                                   frames=range(1, max_ts+2), 
                                   interval=500,
                                   repeat=False,
                                   fargs=(data, network, ax, max_ts))

    # Toggle animation
    paused = False

    def toggle_pause(e):
        nonlocal paused
        if paused:
            anim.resume()
        else:
            anim.pause()
        paused = not paused

    fig.canvas.mpl_connect('button_press_event', toggle_pause)

    # Save animation to a `.gif`
    # anim.save('sim_animation.gif', writer='imagemagick')
    writer = animation.FFMpegWriter(fps=2)
    anim.save("sim_animation.mp4", writer=writer, dpi=100)

    plt.show()


%matplotlib ipympl
if __name__ == "__main__":

    animate()