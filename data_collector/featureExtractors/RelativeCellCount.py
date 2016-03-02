import os
from FeatureExtractorAbstract import FeatureExtractorAbstract
from ..helpers.pathConfig import PathConfig
from ..helpers.voxelData import VoxelData
from ..helpers.utilities import get_before_after_vox

class RelativeCellCount(FeatureExtractorAbstract):
    def getCSVheader(self):
        return ["relCellCountFat", "relCellCountMuscleBefore", "relCellCountBoneBefore",  "relCellCountMuscleAfter", "relCellCountBoneAfter"]

    def extract(self, args):
        output = ['NA'] * 5
        
        if args['voxelBefore'].isValid:
            vd = args['voxelBefore']
            relCountBefore = vd.getRelCounts()
            output[0] = relCountBefore["fat"]
            output[1] = relCountBefore["muscle"]
            output[2] = relCountBefore["bone"]
            
        if args['voxelAfter'].isValid:
            vd = args['voxelAfter']
            relCountAfter = vd.getRelCounts()
            output[3] = relCountAfter["muscle"]
            output[4] = relCountAfter["bone"]
        
        return output
