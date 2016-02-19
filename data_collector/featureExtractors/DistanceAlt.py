import os
from FeatureExtractorAbstract import FeatureExtractorAbstract
from ..helpers.config import PathConfig
from ..helpers.getAltFile import GetAltFile
from ..helpers.distanceCalc import DistanceCalc

class DistanceAlt(FeatureExtractorAbstract):
    def getCSVheader(self):
        return ['euclideanStepAlt', 'manhattanStepAlt', 'euclideanTotalAlt', 'manhattanTotalAlt']

    def extract(self, experiment, type, indiv, arena_size):
        filepath = GetAltFile.getAltTraceFile(experiment, type, indiv)
        if filepath:
            dc = DistanceCalc(arenaSize = (arena_size['x'], arena_size['y']))
            distEuclideanStep = dc.distanceStep(filepath, "euclidean")
            distManhattanStep = dc.distanceStep(filepath, "manhattan")
            distEuclideanTotal = dc.distanceTotal(filepath, "euclidean")
            distManhattanTotal = dc.distanceTotal(filepath, "manhattan")
            return [distEuclideanStep, distManhattanStep, distEuclideanTotal, distManhattanTotal]
        else:
            print "WARN: couldn't find alt trace file for experiment {}, indiv {}".format(experiment[0], indiv[0])
            return ["NA"] * 4
