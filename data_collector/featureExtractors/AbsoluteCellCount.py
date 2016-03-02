from FeatureExtractorAbstract import FeatureExtractorAbstract

class AbsoluteCellCount(FeatureExtractorAbstract):
    def getCSVheader(self):
        return ["absCellCountFat", "absCellCountMuscleBefore", "absCellCountBoneBefore", "absCellCount", "absCellCountMuscleAfter", "absCellCountBoneAfter"]

    def extract(self, args):
        output = ['NA'] * 6
        absCountBefore = args['voxelBefore'].getAbsCounts()
        output[0] = absCountBefore["fat"]
        output[1] = absCountBefore["muscle"]
        output[2] = absCountBefore["bone"]
        output[3] = sum(absCountBefore.values())
            
        absCountAfter = args['voxelAfter'].getAbsCounts()
        output[4] = absCountAfter["muscle"]
        output[5] = absCountAfter["bone"]
        
        return output
