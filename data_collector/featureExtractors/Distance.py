import os
from FeatureExtractorAbstract import FeatureExtractorAbstract
from ..helpers.distanceCalc import DistanceCalc
from ..helpers.utilities import *


class Distance(FeatureExtractorAbstract):
    def getCSVheader(self):
        return ['distanceBefore', 'distanceAfter', 'displacementBefore', 'displacementAfter']

    def extract(self, args):
        traces_before = args['tracesBefore']
        traces_after = args['tracesAfter']
        
        dc = DistanceCalc(arenaSize = (args['arena_size']['x'], args['arena_size']['y']))
        
        if len(traces_before):
            before_disp = dc.displacement(traces_before)
            before_dist = dc.distance(traces_before)
        else:
            before_disp = "NA"
            before_dist = "NA"
        
        if len(traces_after):
            after_disp = dc.displacement(traces_after)
            after_dist = dc.distance(traces_after)
        else:
            after_disp = "NA"
            after_dist = "NA"

        return [before_dist, after_dist, before_disp, after_disp]
