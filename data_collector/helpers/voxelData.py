from __future__ import division
import xml.etree.cElementTree as ET
import numpy as np

def splitEveryN(line, n):
    return [line[i:i + n] for i in range(0, len(line), n)]

class VoxelData:
    root = None
    types = {
        "fat": [1],
        "bone": [2],
        "muscle": [3, 4]
    }
    
    def __init__(self, filename):
        try:
            tree = ET.ElementTree(file=filename)
            self.root = tree.getroot()
            self.isValid = True
        except (ET.ParseError, IOError) as e:
            self.isValid = False

    def getLifeTime(self):
        if not self.isValid:
            return None
        return self.root.find('Simulator').find('StopCondition').find('StopConditionValue').text


    def getDNA(self):
        if not self.isValid:
            return None
        layers = self.root.find('VXC').find('Structure').find('Data').findall('Layer')
        dna = ""
        for layer in layers:
            dna += str(layer.text).strip()
        return dna

    def getDNAmatrix(self):
        dna = self.getDNA()
        if not dna:
            return None
        dnaRows = splitEveryN(dna, 100)
        dnaCols = [splitEveryN(layer, 10) for layer in dnaRows]
        dnaMatrix = np.asarray([[splitEveryN(row, 1) for row in column] for column in dnaCols])
        return dnaMatrix

    @staticmethod
    def _splitEveryN(line, n):
        return [line[i:i + n] for i in range(0, len(line), n)]

    def getAbsCounts(self):
        dna = self.getDNA()
        out = {}
        for typeName, typeNumbers in self.types.iteritems():
            out[typeName] = 0
            for tn in typeNumbers:
                if not dna:
                    out[typeName] = None
                    continue
                out[typeName] += dna.count(str(tn))
        return out

    def getRelCounts(self):
        absCounts = self.getAbsCounts()
        if not absCounts:
            return None
        out = {}
        totalCount = sum(absCounts.values())
        for typeName, typeNumbers in absCounts.items():
            out[typeName] = typeNumbers / totalCount
        return out
