# %% 

%matplotlib ipympl

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt 
import matplotlib.animation as animation
import random


# G = nx.Graph()
# G.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8, 9])
# G.add_edges_from([(1, 2), (3, 4), (2, 5), (4, 5), (6, 7), (8, 9),
#                  (4, 7), (1, 7), (3, 5), (2, 7), (5, 8), (2, 9), (5, 7)])

# def animate(i):
#     colors = ["r", "b", "g", "y", "w", "m"]
#     nx.draw_circular(G, node_color=[random.choice(colors) for j in range(9)])

# nx.draw_circular(G)
# fig = plt.gcf()

# anim = animation.FuncAnimation(fig, animate, frames=20, interval=20, blit=True)



# %% 
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import networkx as nx

G = nx.DiGraph()
G.add_edges_from([(1, 2), (1, 3), (2, 3)])
pos = nx.spring_layout(G)
arcs = nx.draw(G, pos=pos, edge_color="red", 
               width=3, alpha=0.5, style="--")
nx.draw_networkx_edge_labels(G, 
                            edge_labels={
                             (1, 2): "E1", 
                             (1, 3): "E2"}, 
                             font_color="blue")

# arc.set(linewidth=3, edgecolor="r", linestyle="--", alpha=0.5)


# %%
