from __future__ import division
from FeatureExtractorAbstract import FeatureExtractorAbstract
from ..helpers.voxelData import VoxelData
from ..helpers.utilities import *
import math


def calc_tissue_complexity(vd):
    if not vd.isValid:
            return 'NA'
    dnaMatrix = vd.getDNAmatrix().astype(int)

    H = 0
    total = 1000
    for i in range(5):
        count = (dnaMatrix == i).sum()
        p_i = count/total
        if p_i == 0:
            H -= 0
        else:
            H -= p_i * math.log(p_i,2)

    return H



class TissueComplexity(FeatureExtractorAbstract):
    def getCSVheader(self):
        return ['TissueComplexityBefore', 'TissueComplexityAfter']

    def extract(self, args):
        return [calc_tissue_complexity(args['voxelBefore']), calc_tissue_complexity(args['voxelAfter'])]

        




