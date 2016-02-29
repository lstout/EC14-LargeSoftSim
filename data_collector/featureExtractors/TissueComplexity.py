from __future__ import division
from FeatureExtractorAbstract import FeatureExtractorAbstract
from ..helpers.getVoxelData import VoxelData
import os
from ..helpers.config import PathConfig
import math


def calc_tissue_complexity(filepath):
    if not os.path.isfile(filepath):
            return 'NA'
    vd = VoxelData(filepath)
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

    def extract(self, experiment, type, indiv, arena_size):
        if type == 'no disease':
            before = experiment[1] + os.path.sep + PathConfig.populationFolderNormal + os.path.sep + indiv[0] + "_vox.vxa"
        else:
            before = experiment[1] + os.path.sep + PathConfig.populationFoldersAlt[type] + os.path.sep + indiv[0] + "_vox.vxa"

        if type == 'no disease':
            after = experiment[1] + os.path.sep + PathConfig.populationFoldersAlt[type] + os.path.sep + indiv[0] + "_vox.vxa"
        else:
            after = experiment[1] + os.path.sep + PathConfig.populationFolderNormal + os.path.sep + indiv[0] + "_vox.vxa"
        
        return [calc_tissue_complexity(before), calc_tissue_complexity(after)]

        




