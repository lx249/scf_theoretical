# %% 

import matplotlib.pyplot as plt
%matplotlib ipympl

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt 
import matplotlib.animation as animation
import random


class PauseAnimation:
    def __init__(self):
        fig, ax = plt.subplots()
        ax.set_title('Click to pause/resume the animation')
        x = np.linspace(-0.1, 0.1, 1000)

        # Start with a normal distribution
        self.n0 = (1.0 / ((4 * np.pi * 2e-4 * 0.1) ** 0.5)
                   * np.exp(-x ** 2 / (4 * 2e-4 * 0.1)))
        self.p, = ax.plot(x, self.n0)

        self.animation = animation.FuncAnimation(
            fig, self.update, frames=200, interval=50, blit=True)
        self.paused = False

        fig.canvas.mpl_connect('button_press_event', self.toggle_pause)

    def toggle_pause(self, *args, **kwargs):
        if self.paused:
            self.animation.resume()
        else:
            self.animation.pause()
        self.paused = not self.paused

    def update(self, i):
        self.n0 += i / 100 % 5
        self.p.set_ydata(self.n0 % 20)
        return (self.p,)


pa = PauseAnimation()
plt.show()

# %% Animate the simulation.
class SimulationAnimation(object):

    def __init__(self, network, frames, interval=50, blit=True):
        fig, ax = network.draw()
        ax.set_title("Supply Chain Financing Simulation")
        self.animation = animation.FuncAnimation(
            fig, self.update, frames=frames, interval=50, blit=True)
        self.paused = False
        fig.canvas.mpl_connect('button_press_event', self.toggle_pause)
    

    def toggle_pause(self. *args, **kwargs):
        if self.paused:
            self.animation.resume()
        else:
            self.animation.pause()
        self.paused = not self.paused
        self
    

    def update(self, frame):
        pass