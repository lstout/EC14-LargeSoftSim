import os
import types
from FeatureExtractorAbstract import FeatureExtractorAbstract
from ..helpers.config import PathConfig
from ..helpers.getVoxelData import VoxelData


class SizeOnAxis(FeatureExtractorAbstract):
    def getCSVheader(self):
        return ['sizeXmax', 'sizeYmax', 'sizeZmax', 'sizeXmin', 'sizeYmin', 'sizeZmin']

    def extract(self, experiment, variant, indiv, arena_size):
        filepath = experiment[2] + os.path.sep + PathConfig.populationFolderNormal + os.path.sep + indiv[0] + "_vox.vxa"

        if os.path.isfile(filepath):
            vd = VoxelData(filepath)
            dnaMatrix = vd.getDNAmatrix()
            if dnaMatrix is False:
                return ['NA'] * 6

            dnaMatrix = dnaMatrix.astype(int)
            mask = dnaMatrix > 0
            z = mask.sum(axis=0)
            y = mask.sum(axis=1)
            x = mask.sum(axis=2)

            return [x.max(), y.max(), z.max(), x.min(), y.min(), z.min()]

        else:
            return ['NA'] * 6
