# %% 
import networkx as nx
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt 
import matplotlib.animation as animation

from network import SCNetwork


def get_data_at_t(data, timestep):
    """
    Get data at the given time step.
    """
    return data[data.timestep == timestep]


def get_orders(data):
    # Select the rows in which nodes has incoming orders
    rows_w_order = data[~data["order_from"].isna()]
    orders = {}
    for i, row in rows_w_order.iterrows():
        buyer, seller = row["order_from"], row["node_idx"]
        orders[(buyer, seller)] = int(row["buy_amount"])
    return orders


# Return the list of bankrupt nodes
def get_bankrupt_nodes(data):
    bankrupt_nodes = data.loc[data.is_bankrupt == True, ["node_idx"]]
    return list(bankrupt_nodes["node_idx"])


def update(ts, data, network, ax):
    ax.clear()

    G, layout = network.G, network.layout
    node_colors, node_labels = network.node_colors, network.node_labels

    # Update at current time step
    data_at_t = get_data_at_t(data, ts)
    orders = get_orders(data_at_t)
    bankrupt_nodes = get_bankrupt_nodes(data_at_t)
    for node_idx in bankrupt_nodes:
        node_colors[node_idx] = "red"
        ebunch = list(G.in_edges(node_idx)) + list(G.out_edges(node_idx))
        G.remove_edges_from(ebunch)

    # Styling
    graph_options = network.config["graph_options"]
    edge_options = network.config["edge_options"]
    edge_label_options = network.config["edge_label_options"]

    # Plotting
    add_info = "" if not bankrupt_nodes else f": node(s) {', '.join(map(str, bankrupt_nodes))} bankrupted"
    ax.set_title(f"[Time step {ts}] {add_info}")
    nx.draw_networkx(G, layout, node_color=node_colors, labels=node_labels, **graph_options)
    nx.draw_networkx_edges(G, layout, edgelist=list(orders.keys()), **edge_options)
    nx.draw_networkx_edge_labels(G, layout, edge_labels=orders, **edge_label_options)


def animate():
    # Data preparation
    data_file = "output_data/output__sim_0.csv"
    data = pd.read_csv(data_file)

    max_timestep = data.timestep.max()

    network = SCNetwork(config_file="configs/network_config.yaml")
    fig, ax = network.draw()

    # Remove frames 
    for pos in ["top", "left", "bottom", "right"]:
        ax.spines[pos].set_visible(False)

    anim = animation.FuncAnimation(fig, update, 
                                   frames=range(1, max_timestep+1), 
                                   interval=500, 
                                   fargs=(data, network, ax))
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
    anim.save("sim_animation.mp4", writer=writer)

    plt.show()


%matplotlib ipympl
if __name__ == "__main__":

    animate()
    

    



