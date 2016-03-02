import os
from FeatureExtractorAbstract import FeatureExtractorAbstract
from ..helpers.distanceCalc import DistanceCalc
from ..helpers.utilities import *


class Distance(FeatureExtractorAbstract):
    def getCSVheader(self):
        return ['distanceBefore', 'distanceAfter']

    def extract(self, args):
        traces_before = args['tracesBefore']
        traces_after = args['tracesAfter']
        
        dc = DistanceCalc(arenaSize = (args['arena_size']['x'], args['arena_size']['y']))
        
        if len(traces_before):
            before_dist = dc.distance(traces_before)
        else:
            before_dist = "NA"
        
        if len(traces_after):
            after_dist = dc.distance(traces_after)
        else:
            after_dist = "NA"

        return [before_dist, after_dist]
