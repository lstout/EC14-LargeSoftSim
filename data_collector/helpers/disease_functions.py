import xml.etree.cElementTree as ET
import random
import sys
import numpy as np

def get_tree(filename):
    tree = ET.ElementTree(file=filename)
    return tree

def get_layers(tree):
    root = tree.getroot()
    layers = root.find('VXC').find('Structure').find('Data').findall('Layer')
    return layers

def get_dna(layers):
    dna = [map(int,list(layer.text.strip())) for layer in layers]
    return np.array(dna)

def read_dna_file(fp):
    tree = get_tree(fp)
    layers = get_layers(tree)
    return get_dna(layers)

def write_dna(dna_new, fp):
    tree = get_tree(fp)
    layers = get_layers(tree)
    
    for i, layer in enumerate(layers):
        layer.text = "".join(map(str,dna_new[i]))
    try:
        tree.write(fp)
    except Exception as e:
        print 'HN ERROR:', type(e), e
        raise

def coin_flip(dna):
    return 0.5

def mutate_all(dna):
    return 1

def sigmoid_fat(dna):
    pass

def default_prob_per_fat(dna):
    return (dna == 1).sum() * 0.005

def double_prob_per_fat(dna):
    return (dna == 1).sum() * 0.01

def very_high_prob_per_fat(dna):
    return (dna == 1).sum() * 0.05


def apply_disease(fp, indiv_func = mutate_all, cell_fun = default_prob_per_fat):
        """
        Mutates muscle tissue voxels according to some probability in each layer
        """
        dna = read_dna_file(fp)
        if indiv_func(dna) <= random.random():
            return
        
        p = cell_fun(dna)
        dna_new = np.copy(dna)
        rand = np.random.rand((dna_new >= 3).sum())
        n = 0
        for i in range(dna_new.shape[0]):
            for j in range(dna_new.shape[1]):
                if dna[i,j] >= 3:
                    if rand[n] < p:
                        dna[i,j] = 2
                    n += 1
        write_dna(dna_new, fp)
