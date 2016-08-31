import numpy as np
import math
import sys
import os

class DistanceCalc:
    def __init__(self, **kwargs):
        self.arenaSize = kwargs.get("arenaSize", (0.25, 0.25))

    def distance(self, traces):
        xs = traces[1,:]
        ys = traces[2,:]
        x_diff = np.fmin(np.abs(xs[:-1] - xs[1:]), self.arenaSize[0] - np.abs(xs[:-1] - xs[1:]))
        y_diff = np.fmin(np.abs(ys[:-1] - ys[1:]), self.arenaSize[1] - np.abs(ys[:-1] - ys[1:]))
        return np.sqrt(x_diff**2 + y_diff**2).sum()
   
    def displacement(self, traces):
        x_diff = min(abs(traces[1,-1] - traces[1,0]), self.arenaSize[0] - abs(traces[1,-1] - traces[1,0]))
        y_diff = min(abs(traces[2,-1] - traces[2,0]), self.arenaSize[0] - abs(traces[2,-1] - traces[2,0]))
        return math.sqrt(x_diff**2 + y_diff**2)

