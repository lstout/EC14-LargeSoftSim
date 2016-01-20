import os
import sys

expFolder = "~/EC14-Experiments"
libFolder = "~/lib"


def _makeFolderIfNotExists(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print "INFO: Done"
    else:
        print "WARN: Directory already exists"


def makeExpFolder():
    expFolderPath = os.path.expanduser(expFolder)

    print "INFO: Creating Experiment Folder: " + expFolderPath
    _makeFolderIfNotExists(expFolderPath)


def makeVoxelyze():
    libFolderPath = os.path.expanduser(libFolder)

    print "INFO: === Preparing Voxelyze Robot Simulator ==="
    print "INFO: Creating library directory: " + libFolderPath

    _makeFolderIfNotExists(libFolderPath)
    


makeExpFolder()
makeVoxelyze()
