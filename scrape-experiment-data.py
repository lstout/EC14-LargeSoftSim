import csv
import glob
import re
import os
import cPickle as pickle
from data_collector.featureExtractors import *
from data_collector.helpers.pathConfig import PathConfig
import ConfigParser
from data_collector.helpers.utilities import get_voxels, get_traces
import multiprocessing

__author__ = 'meta'

docString = """ DataCollector 2 main script (rewrite of the original)

This script can be run standalone with 2 optional command line parameters:
[output file name] - (string, default: 'data.csv'), this defines the filename of the CSV output that this script generates
[search pattern] - (string, default: '../EC14-Exp-*'), this defines what folders are searched. Can also be set to "null" to use the default
[limit] - (integer, default: no limit) max number of individuals to get for each experiment
[continue] - (string, default: false) if this is "continue" or "true", then the data collection will not repeat completed experiments
"""

def _pickle_method(method):
    func_name = method.im_func.__name__
    obj = method.im_self
    cls = method.im_class
    return _unpickle_method, (func_name, obj, cls)

def _unpickle_method(func_name, obj, cls):
    for cls in cls.mro():
        try:
            func = cls.__dict__[func_name]
        except KeyError:
            pass
        else:
            break
    return func.__get__(obj, cls)

import copy_reg
import types
copy_reg.pickle(types.MethodType, _pickle_method, _unpickle_method)


class DataCollector2(object):
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
            Disease(),
            Lifetime(),
            Distance(),
            AbsoluteCellCount(),
            RelativeCellCount(),
            MuscleLocation(),
            Gait(),
            ShapeComplexity(),
            TissueComplexity(),
            Birthtime(),
            Cost(),
        ]
        self.pickleLocation = os.path.dirname(
            os.path.realpath(__file__)) + os.path.sep + "progress.pickle"

    def getExperiments(self):
        expFolders = glob.glob(os.path.expanduser(self.pattern))
        output = [(expFolder.split('/')[-1] , expFolder) 
                for expFolder in expFolders if os.path.isdir(expFolder)]
        return output

    def processExp(self, exp):
        exp_type = self.getType(exp)
        if not exp_type:
            return [] 
        individuals = self.getIndividuals(exp)
        print "parsing experiment {exp} (type: {exp_type}) with {indivs} individuals".format(
            exp=exp[0],
            exp_type=exp_type,
            indivs=len(individuals)
        )
        features = [] 
        args = {}
        args['exp_type'] = exp_type
        args['exp'] = exp
        args['config'] = self.getConfig(args)
        args['arena_size'] = self.getArenaSize(args['config'])        
        for count, indiv in enumerate(individuals[:self.limit]):
            args['indiv'] = indiv
            args['voxelBefore'], args['voxelAfter'] = get_voxels(args)
            args['tracesBefore'], args['tracesAfter'] = get_traces(args)
            features.append( self.getFeatures(args) )
            self.printExperimentProgress(min(len(individuals), self.limit), count)
        return features


    def collectData(self):
        experiments = self.getExperiments()
        
        print "I found the following experiments: \n", [exp[0] for exp in experiments]
        if os.path.exists(self.outputFile):
	    os.remove(self.outputFile)
        self.printHeaders() 
        
        pool = multiprocessing.Pool(10)
        features = [ feature for exp in pool.map(self.processExp, experiments) for feature in exp ]
        self.writeFeatures(features)

        print "wrote {} lines to {}".format(len(features), self.outputFile)

    def filterExperiments(self, experiments, experimentsDone):
        out = [experiment for experiment in experiments if experiment not in experimentsDone]
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
   	return None
 
    def getConfig(self, args):
        with open(args['exp'][1] + "/config/config.ini") as fh:
            cp = ConfigParser.RawConfigParser()
            cp.readfp(fh)
        return cp


    def getArenaSize(self, cp):
        arena_size = {}
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

    def getFeatures(self, args):
        return [f for feature in self.featureExtractors for f in feature.extract(args)]

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
