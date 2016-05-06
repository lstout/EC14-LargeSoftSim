import os
from FeatureExtractorAbstract import FeatureExtractorAbstract
from ..helpers.pathConfig import PathConfig
from ..helpers.voxelData import VoxelData
from ..helpers.utilities import get_before_after_trace


class Birthtime(FeatureExtractorAbstract):
    def getCSVheader(self):
        return ['birthtime']

    def extract(self, args):
        if args['exp_type'] == 'no disease':
            traces = args['tracesBefore']
        else:
            traces = args['tracesAfter']
        if len(traces):
            try:
                return [traces[0,0]]
            except IndexError:
                return ['NA']
        else:
            return ['NA']
