import csv
import glob
import re
import os
import cPickle as pickle
from data_collector.featureExtractors import *
from data_collector.helpers.config import PathConfig
import ConfigParser

__author__ = 'meta'

docString = """ DataCollector 2 main script (rewrite of the original)

This script can be run standalone with 2 optional command line parameters:
[output file name] - (string, default: 'data.csv'), this defines the filename of the CSV output that this script generates
[search pattern] - (string, default: '../EC14-Exp-*'), this defines what folders are searched. Can also be set to "null" to use the default
[limit] - (integer, default: no limit) max number of individuals to get for each experiment
[continue] - (string, default: false) if this is "continue" or "true", then the data collection will not repeat completed experiments
"""


class DataCollector2:
    def __init__(self, pattern, outputFile, limit, cont):
        self.pattern = pattern
        self.outputFile = outputFile
        self.limit = limit
        self.cont = cont

        print "Using the following parmeters:\n" \
              "pattern: {pattern}\n" \
              "output file: {outfile}\n" \
              "limit: {limit}\n" \
              "continue: {cont}".format(
            pattern=self.pattern,
            outfile=self.outputFile,
            limit=self.limit,
            cont=self.cont
        )

        self.previousPercentDone = 0

        self.featureExtractors = [
            BasicInfo(),
            MutProbability(),
            Lifetime(),
            DistanceOriginal(),
            DistanceAlt(),
            AbsoluteCellCountOriginal(),
            RelativeCellCountOriginal(),
            AbsoluteCellCountAlt(),
            RelativeCellCountAlt(),
            SizeOnAxis(),
            RelHeight(),
            MuscleLocation(),
            Symmetry(),
            Arc(),
            Monotony(),
            Gait(),
            ShapeComplexity(),
            TissueComplexity(),
            Birthtime(),
        ]
        self.pickleLocation = os.path.dirname(
            os.path.realpath(__file__)) + os.path.sep + "progress.pickle"

    def getExperiments(self):
	print self.pattern
        expFolders = glob.glob(self.pattern)
        print expFolders
        output = [(os.path.basename(expFolder),
                   expFolder) for expFolder in expFolders if os.path.isdir(expFolder)]
        return output

    def collectData(self):
        experiments = self.getExperiments()
        experimentsDone = self.loadProgress()
        self.printHeaders()        

        print "I found the following experiments: \n", [exp[0] for exp in experiments]
        if self.cont:
            experiments = self.filterExperiments(experiments, experimentsDone)
            print "I will only parse the following experiments :\n", \
                [exp[0] for exp in experiments]

        row_count = 0 
        for exp in experiments:
            type = self.getType(exp)
            arena_size = self.getArenaSize(exp)
            individuals = self.getIndividuals(exp)
            print "parsing experiment {exp} (type: {type}) with {indivs} individuals".format(
                exp=exp[0],
                type=type,
                indivs=len(individuals)
            )
            features = [] 
            for count, indiv in enumerate(individuals[:self.limit]):
                features.append( self.getFeatures(exp, type, indiv, arena_size) )
                self.printExperimentProgress(min(len(individuals), self.limit), count)
            self.writeFeatures(features)
            experimentsDone = self.saveProgress(exp, experimentsDone)
            row_count += len(individuals[:self.limit])

        print "wrote {} lines to {}".format(row_count, self.outputFile)

    def saveProgress(self, experiment, experimentsDone):
        experimentsDone.append(experiment)
        pickle.dump(experimentsDone, open(self.pickleLocation, "wb"))
        return experimentsDone

    def loadProgress(self):
        try:
            return pickle.load(open(self.pickleLocation, "r+"))
        except (EOFError, IOError) as e:
            print type(e), e
            return []

    def filterExperiments(self, experiments, experimentsDone):
        out = [experiment for experiment in experiments if experiment not in experimentsDone]
        #print out
        return out

    def getIndividuals(self, experiment):
        indivs = glob.glob(experiment[1] + os.path.sep + PathConfig.populationFolderNormal + os.path.sep + "*.vxa")
        output = [(os.path.basename(indiv).split("_")[0], indiv) for indiv in indivs]
        output.sort(key=lambda x: int(x[0]))
        return output

    def getType(self, experiment):
        # if the alternative population DOES have a disease then the main experiment DIDN'T have a disease
        if self.hasAltPop(experiment, "with disease"):
            if not self.hasAltPop(experiment, "no disease"):
                return "with disease"
            else:
                self.errorHasBothPopFiles(experiment)
        # if the alternative population DOESN'T have a disease then the main experiment DID have a disease
        if self.hasAltPop(experiment,"no disease"):
            if not self.hasAltPop(experiment, "with disease"):
                return "no disease"
            else:
                self.errorHasBothPopFiles(experiment)
        # if neither is the case, then there are no population files for this experiment... abort
        self.errorHasNoPop(experiment)

    def getArenaSize(self, experiment):
        arena_size = {}
        with open(experiment[1] + "/config/config.ini") as fh:
            cp = ConfigParser.RawConfigParser()
            cp.readfp(fh)
            x = cp.getfloat('Arena', 'x')
            y = cp.getfloat('Arena', 'y')
            if x == 0.25 and y == 0.25:
                arena_size['name'] = 'small'
            elif x == 0.5 and y == 0.5:
                arena_size['name'] = 'big'
            else:
                arena_size['name'] = 'unknown'
            arena_size['x'] = x
            arena_size['y'] = y
        return arena_size

    def hasAltPop(self, experiment, condition):
        altPopPath = experiment[1] + os.path.sep + PathConfig.populationFoldersAlt[condition]
        if not os.path.isdir(altPopPath):
            return False
        if len(os.listdir(altPopPath)) > 0:
            return True
        return False

    def getFeatures(self, experiment, type, indiv, arena_size):
        output = []
        for feature in self.featureExtractors:
            output += feature.extract(experiment, type, indiv, arena_size)
        return output

    def printExperimentProgress(self, total, current):
        percentDone = round(100 * current * 1.0 / total)
        if percentDone != self.previousPercentDone:
            sys.stdout.write('{}% done\r'.format(int(percentDone)))
            sys.stdout.flush()
            self.previousPercentDone = percentDone

    def writeFeatures(self, features):
        with open(self.outputFile, 'a') as fh:
            for f in features:
                f = map(str, f)
                fh.write(",".join(f) + "\n")
            
    def printHeaders(self):
        headers = [header for feature in self.featureExtractors for header in feature.getCSVheader()]
        headersString = ','.join(headers)
        headerNotWritten = False
        with open(self.outputFile, "a+") as fh:
            fh.seek(0)
            l = fh.readline().strip()
            if not headersString == l:
                headerNotWritten = True
        if headerNotWritten:
            with open(self.outputFile, "w") as fh:
                fh.write(headersString + "\n")
        return headers 

    @staticmethod
    def errorHasBothPopFiles(experiment):
        print "ERROR: this shouldn't happen - an experiment has alternative population files " \
              "both WITH and WITHOUT disease in addition to the normal experiment traces:"
        print experiment
        print "...Please fix this before continuing. Exiting."
        quit()

    @staticmethod
    def errorHasNoPop(experiment):
        print "ERROR: the following experiment has no alternative population files (neither with disease nor without):"
        print experiment
        print "...Please fix this before continuing. Exiting."
        quit()


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1:
        print docString
        quit()

    pattern = '../EC14-Exp-*'
    limit = int(1e6)
    con = False
    
    outputFile = sys.argv[1]
    if len(sys.argv) >= 3:
        pattern = sys.argv[2]
        if pattern.lower() == "null" or pattern.lower() == "false":
            pattern = False
    if len(sys.argv) >= 4:
        limit = int(sys.argv[3])
    if len(sys.argv) == 5:
        cont = sys.argv[4]
        if cont.lower() in ["cont", "continue", "c", "true", "y"]:
            con = True
        else:
            con = False

    dataCol = DataCollector2(pattern, outputFile, limit, con)
    dataCol.collectData()
