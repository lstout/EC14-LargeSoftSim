import os
from FeatureExtractorAbstract import FeatureExtractorAbstract
from ..helpers.distanceCalc import DistanceCalc


class DistanceOriginal(FeatureExtractorAbstract):
    def getCSVheader(self):
        return ['euclideanStep', 'manhattanStep', 'euclideanTotal', 'manhattanTotal']

    def extract(self, experiment, type, indiv, arena_size):
        filepath = experiment[2] + os.path.sep + "traces_afterPP" + os.path.sep + indiv[0] + ".trace"
        if os.path.isfile(filepath):
            dc = DistanceCalc(arenaSize = (arena_size['x'], arena_size['y']))
            distEuclideanStep = dc.distanceStep(filepath, "euclidean")
            distManhattanStep = dc.distanceStep(filepath, "manhattan")
            distEuclideanTotal = dc.distanceTotal(filepath, "euclidean")
            distManhattanTotal = dc.distanceTotal(filepath, "manhattan")
            return [distEuclideanStep, distManhattanStep, distEuclideanTotal, distManhattanTotal]
        else:
            return ["NA"] * 4
