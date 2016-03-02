import os
from pathConfig import PathConfig
from voxelData import VoxelData
import ConfigParser
import numpy as np

def get_before_after_vox(exp_name, exp_type, indiv_id):
    prefix = exp_name + os.path.sep
    suffix = os.path.sep + indiv_id + "_vox.vxa"
    if exp_type == 'no disease':
        before = PathConfig.populationFolderNormal
        after = PathConfig.populationFoldersAlt[exp_type]        
    else:
        before = PathConfig.populationFoldersAlt[exp_type]
        after = PathConfig.populationFolderNormal
        
    before = prefix + before + suffix
    after = prefix + after + suffix
    return before, after

def get_before_after_trace(exp_name, exp_type, indiv_id):
    prefix = exp_name + os.path.sep
    suffix = os.path.sep + indiv_id + ".trace"
    
    if exp_type == 'no disease':
        before = PathConfig.traceFolderNormal
        after = PathConfig.traceFoldersAlt[exp_type]        
    else:
        before = PathConfig.traceFoldersAlt[exp_type]
        after = PathConfig.traceFolderNormal
        
    before = prefix + before + suffix
    after = prefix + after + suffix
    return before, after

def get_config_attr(exp_name, section, name):
    cp = ConfigParser.RawConfigParser()
    fn = exp_name + os.path.sep + 'config' + os.path.sep + 'config.ini'
    cp.read(fn)
    try:
        return cp.get(section, name)
    except ConfigParser.NoSectionError as e:
        return None

def get_voxels(args):
    before, after = get_before_after_vox(args['exp'][1], args['exp_type'], args['indiv'][0])
    return VoxelData(before), VoxelData(after)

def get_traces_file(fn):
    if not os.path.isfile(fn):
        return []
    with open(fn) as fh:
        time = []
        xs = []
        ys = []
        zs = []
        for line in fh:
            line = line.split()
            try:
                t = float(line[1])
                x = float(line[2])
                y = float(line[3])
                z = float(line[4])
                time.append(t)
                xs.append(x)
                ys.append(y)
                zs.append(z)
            except (IndexError, ValueError) as e:
                continue

    return np.array([time, xs, ys, zs])

def get_traces(args):
    before, after = get_before_after_trace(args['exp'][1], args['exp_type'], args['indiv'][0])
    traces_before = get_traces_file(before)
    traces_after = get_traces_file(after)
    return traces_before, traces_after


