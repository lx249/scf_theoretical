# %% 

import matplotlib.pyplot as plt
%matplotlib ipympl

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt 
import matplotlib.animation as animation
import random

nodes = [1, 2, 3, 4, 5, 6, 7, 8, 9]
edges = [(1, 2), (3, 4), (2, 5), (4, 5), (6, 7), (8, 9),
         (4, 7), (1, 7), (3, 5), (2, 7), (5, 8), (2, 9), (5, 7)]
G = nx.Graph()

G.add_nodes_from(nodes)
G.add_edges_from(edges)
pos = nx.spring_layout(G)

nx.draw(G, pos=pos)
fig = plt.gcf()
ax = plt.gca()

# def animate(i):
#     print(edges[i])
#     nx.draw_networkx_edges(G, pos=pos, 
#                             edgelist=[edges[i]], width=3, edge_color="red", alpha=0.5)


# anim = animation.FuncAnimation(fig, animate, frames=range(len(edges)), interval=5000, blit=True)


# class PauseAnimation:
#     def __init__(self):
#         fig, ax = plt.subplots()
#         ax.set_title('Click to pause/resume the animation')
#         x = np.linspace(-0.1, 0.1, 1000)

#         # Start with a normal distribution
#         self.n0 = (1.0 / ((4 * np.pi * 2e-4 * 0.1) ** 0.5)
#                    * np.exp(-x ** 2 / (4 * 2e-4 * 0.1)))
#         self.p, = ax.plot(x, self.n0)

#         self.animation = animation.FuncAnimation(
#             fig, self.update, frames=200, interval=50, blit=True)
#         self.paused = False

#         fig.canvas.mpl_connect('button_press_event', self.toggle_pause)

#     def toggle_pause(self, *args, **kwargs):
#         if self.paused:
#             self.animation.resume()
#         else:
#             self.animation.pause()
#         self.paused = not self.paused

#     def update(self, i):
#         self.n0 += i / 100 % 5
#         self.p.set_ydata(self.n0 % 20)
#         return (self.p,)


# pa = PauseAnimation()
# plt.show()
