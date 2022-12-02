# %% 
from network import SCNetwork
import networkx as nx
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt 
import matplotlib.animation as animation
import random


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
        orders[(buyer, seller)] = row["buy_amount"]
    return orders


def update(ts, data, network, ax):
    ax.clear()

    # Data for updating
    data_at_t = get_data_at_t(data, ts)
    orders = get_orders(data_at_t)

    # Styling
    graph_options = network.config["graph_options"]
    node_colors = network.config["node_colors"]
    edge_options = network.config["edge_options"]
    edge_label_options = network.config["edge_label_options"]
    node_color = ([node_colors["raw_material"]]
                  + [node_colors["other"]] * (network.G.number_of_nodes() - 2)
                  + [node_colors["market"]])

    G, layout = network.G, network.layout

    nx.draw_networkx(G, layout, node_color=node_color, **graph_options)
    nx.draw_networkx_edges(G, layout, edgelist=list(orders.keys()), **edge_options)
    nx.draw_networkx_edge_labels(G, layout, edge_labels=orders, **edge_label_options)
    ax.set_title(f"Time step {ts}")


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
    anim.save('sim_animation.gif', writer='imagemagick')

    plt.show()


%matplotlib ipympl
if __name__ == "__main__":

    animate()
    

    



