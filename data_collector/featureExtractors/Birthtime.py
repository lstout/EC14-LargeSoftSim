import os
from FeatureExtractorAbstract import FeatureExtractorAbstract
from ..helpers.config import PathConfig
from ..helpers.getVoxelData import VoxelData


class Birthtime(FeatureExtractorAbstract):
    def getCSVheader(self):
        return ['birthtime']

    def extract(self, experiment, type, indiv, arena_size):
        filepath = experiment[2] + os.path.sep + PathConfig.traceFolderNormal + os.path.sep + indiv[0] + ".trace"
        if os.path.isfile(filepath):
            with open(filepath) as fh:
                line = fh.readline()
                try:
                    birthtime = line.split('\t')[1]
                except Exception as e:
                    birthtime ='NA'

                return [birthtime]
                
        else:
            return ['NA']
