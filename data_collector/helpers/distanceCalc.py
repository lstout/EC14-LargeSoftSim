import numpy as np
import math

class DistanceCalc:
    def __init__(self, **kwargs):
        self.arenaSize = kwargs.get("arenaSize", (0.25, 0.25))

    def isValidLine(self, lineSplit):
        return len(lineSplit) == 5 and self.sameAsFloat(lineSplit[2]) and self.sameAsFloat(lineSplit[3])

    def distanceStep(self, filename, type):
        with open(filename, 'r') as inputFile:
            firstRun = True
            dist = 0
            xs = []
            ys = []
            for line in inputFile:
                lineSplit = line.split("\t")
                if not self.isValidLine(lineSplit):
                    lineSplit = line.split(" ")
                    if not self.isValidLine(lineSplit):
                        continue

                xs.append(float(lineSplit[2]))
                ys.append(float(lineSplit[3]))

            xs = np.array(xs)
            ys = np.array(ys)
            x_diff = np.fmin(np.abs(xs[:-1] - xs[1:]), self.arenaSize[0] - np.abs(xs[:-1] - xs[1:]))
            y_diff = np.fmin(np.abs(ys[:-1] - ys[1:]), self.arenaSize[0] - np.abs(ys[:-1] - ys[1:]))
            if type == 'euclidean':
                return np.sqrt(x_diff**2 + y_diff**2).sum()
            else:
                return (x_diff + y_diff).sum()   

    def distanceTotal(self, filename, type):
        with open(filename, 'r') as inputFile:
            
            firstRun = True
            lineSplit = []
            x_diffs_to_add = []
            y_diffs_to_add = []
            lastLine = None
            
            for line in inputFile:
                lineSplit = line.split("\t")
                if not self.isValidLine(lineSplit):
                    lineSplit = line.split(" ")
                    if not self.isValidLine(lineSplit):
                        continue
                lastLine = lineSplit
                if firstRun:
                    first_x = x_new = float(lineSplit[2])
                    first_y = y_new = float(lineSplit[3])
                    firstRun = False
                else:
                    x, x_new = x_new, float(lineSplit[2])
                    y, y_new = y_new, float(lineSplit[3])
                    x_diff = x - x_new
                    y_diff = y - y_new
                    if abs(x_diff) >= self.arenaSize[0] * 0.8:
                        diff_to_add = self.arenaSize[0]
                        if x_new > x:
                            diff_to_add = -diff_to_add
                        x_diffs_to_add.append(diff_to_add)
                    if abs(y_diff) >= self.arenaSize[1] * 0.8:
                        diff_to_add = self.arenaSize[1]
                        if y_new > y:
                            diff_to_add = -diff_to_add
                        y_diffs_to_add.append(diff_to_add)

            if lastLine is None:
                return 0
            last_x = float(lastLine[2])
            last_y = float(lastLine[3])
            x_final = last_x + sum(x_diffs_to_add)
            y_final = last_y + sum(y_diffs_to_add)

            x_diff = first_x - x_final
            y_diff = first_y - y_final

            if type == "euclidean":
                return math.sqrt((x_diff ** 2) + (y_diff ** 2))
            if type == "manhattan":
                return abs(x_diff) + abs(y_diff)

    @staticmethod
    def getBirthTime(filename):
        with open(filename, 'r') as inputFile:
            for line in inputFile:
                lineSplit = line.split("\t")
                if len(lineSplit) != 5:
                    return False
                else:
                    return float(lineSplit[1])

    @staticmethod
    def sameAsFloat(input):
        try:
            floatInput = float(input)
            return str(floatInput) == str(input)
        except ValueError:
            return False


if __name__ == "__main__":  # this is for testing only
    inFile = "data/1987.pp.trace"
    dc = DistanceCalc()
    print dc.distanceStep(inFile, "euclidean")
    print dc.distanceTotal(inFile, "euclidean")
