import os
import types
import numpy as np
import itertools as it
from FeatureExtractorAbstract import FeatureExtractorAbstract
from ..helpers.config import PathConfig
from ..helpers.getVoxelData import VoxelData


class MuscleLocation(FeatureExtractorAbstract):
    def getCSVheader(self):
        return ['muscleBottom', 'muscleTop', 'muscleCenter', 'muscleOuter', 'muscleCenterRel', 'muscleOuterRel']

    def extract(self, experiment, variant, indiv, arena_size):
        filepath = experiment[2] + os.path.sep + PathConfig.populationFolderNormal + os.path.sep + indiv[0] + "_vox.vxa"

        if not os.path.isfile(filepath):
            return ['NA'] * 6
        vd = VoxelData(filepath)
        dnaMatrix = vd.getDNAmatrix()
        if dnaMatrix is False:
            return ['NA'] * 6
        
        dnaMatrix = dnaMatrix.astype(int)

        bottom = dnaMatrix[:3, :, :]
        muscleBottom = np.sum(np.logical_or(bottom == 3, bottom == 4))
        
        top = dnaMatrix[7:, :, :]
        muscleTop = np.sum(np.logical_or(top == 3, top == 4))

        center = dnaMatrix[3:7, 3:7, 3:7]
        muscleCenter = np.sum(np.logical_or(center == 3, center == 4))
        
        outerIdx = zip(*it.product([0,1,8,9], [0,1,8,9], [0,1,8,9]))
        outer = dnaMatrix[outerIdx]        

        muscleOuter = np.sum(np.logical_or(outer == 3, outer == 4))

        muscleTotal = np.sum(np.logical_or(dnaMatrix == 3, dnaMatrix == 4))

        if muscleTotal > 0:
            muscleCenterRel = float(muscleCenter) / muscleTotal
            muscleOuterRel = float(muscleOuter) / muscleTotal
        else:
            muscleCenterRel = 0.0
            muscleOuterRel = 0.0

        return [muscleBottom, muscleTop, muscleCenter, muscleOuter, muscleCenterRel, muscleOuterRel]
