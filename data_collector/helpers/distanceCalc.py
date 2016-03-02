import numpy as np
import math

class DistanceCalc:
    def __init__(self, **kwargs):
        self.arenaSize = kwargs.get("arenaSize", (0.25, 0.25))

    def distance(self, traces):
        xs = traces[1,:]
        ys = traces[2,:]
        x_diff = np.fmin(np.abs(xs[:-1] - xs[1:]), self.arenaSize[0] - np.abs(xs[:-1] - xs[1:]))
        y_diff = np.fmin(np.abs(ys[:-1] - ys[1:]), self.arenaSize[0] - np.abs(ys[:-1] - ys[1:]))
        return np.sqrt(x_diff**2 + y_diff**2).sum()
