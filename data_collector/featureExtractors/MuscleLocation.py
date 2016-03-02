from __future__ import division
import numpy as np
import itertools as it
from FeatureExtractorAbstract import FeatureExtractorAbstract
from ..helpers.pathConfig import PathConfig
from ..helpers.voxelData import VoxelData
from ..helpers.utilities import get_before_after_vox


class MuscleLocation(FeatureExtractorAbstract):
    def getCSVheader(self):
        return ['muscleBottom', 'muscleTop', 'muscleCenter', 'muscleOuter', 'muscleCenterRel', 'muscleOuterRel']

    def extract(self, args):
        if args['exp_type'] == 'no disease':
            vd = args['voxelBefore']
        else:
            vd = args['voxelAfter']
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

        muscleOuter = int(np.sum(np.logical_or(outer == 3, outer == 4)))
        muscleTotal = int(np.sum(np.logical_or(dnaMatrix == 3, dnaMatrix == 4)))

        if muscleTotal:
            muscleCenterRel = muscleCenter / muscleTotal
            muscleOuterRel = muscleOuter / muscleTotal
        else:
            muscleCenterRel = float('inf')
            muscleOuterRel = float('inf')

        return [muscleBottom, muscleTop, muscleCenter, muscleOuter, muscleCenterRel, muscleOuterRel]
