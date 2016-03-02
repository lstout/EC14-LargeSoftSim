import os
from FeatureExtractorAbstract import FeatureExtractorAbstract
from ..helpers.pathConfig import PathConfig
from ..helpers.voxelData import VoxelData
from ..helpers.utilities import get_before_after_vox


class Lifetime(FeatureExtractorAbstract):
    def getCSVheader(self):
        return ['lifetime']

    def extract(self, args):
        if args['exp_type'] == 'no disease':
            vd = args['voxelBefore']
        else:
            vd = args['voxelAfter']
        lifetime = vd.getLifeTime()
        if not lifetime:
            return ['NA']
        return [lifetime]
