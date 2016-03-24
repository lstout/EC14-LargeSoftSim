from __future__ import division
from FeatureExtractorAbstract import FeatureExtractorAbstract
from ..helpers.voxelData import VoxelData
from ..helpers.utilities import *
import math
import itertools as it


def calc_tissue_complexity(vd):
    if not vd.isValid:
            return 'NA'
    dnaMatrix = vd.getDNAmatrix().astype(int)
    return tc(dnaMatrix)

def tc(matrix):
    H = 0
    total = matrix.size
    for i in range(5):
        count = (matrix == i).sum()
        p_i = count/total
        if p_i == 0:
            H -= 0
        else:
            H -= p_i * math.log(p_i,2)
    return H

        

def mean_tissue_complexity(vd):
    if not vd.isValid:
            return 'NA'
    dnaMatrix = vd.getDNAmatrix().astype(int)
    stepSize = 5
    comps = []
    for x,y,z in it.product(range(0,10,stepSize), range(0,10,stepSize), 
            range(0,10,stepSize)):
        subM = dnaMatrix[x:x+stepSize,y:y+stepSize,z:z+stepSize]
        if not np.any(subM > 0):
            continue
        comps.append(tc(subM))

    return sum(comps)/len(comps)





class TissueComplexity(FeatureExtractorAbstract):
    def getCSVheader(self):
        return ['TissueComplexityBefore', 'TissueComplexityAfter', 'MeanTissueComplexityBefore', 'MeanTissueComplexityAfter']

    def extract(self, args):
        return [calc_tissue_complexity(args['voxelBefore']), calc_tissue_complexity(args['voxelAfter']), mean_tissue_complexity(args['voxelBefore']), mean_tissue_complexity(args['voxelAfter'])]

        




