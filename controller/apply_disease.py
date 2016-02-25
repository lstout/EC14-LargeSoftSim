from __future__ import division
import xml.etree.cElementTree as ET
from random import shuffle
import random
import os
import sys




def atrophyMuscles(path):
    """Mutates muscle tissue voxels according to some probability in each layer
    """
    for dna_file in os.listdir(path):
        if dna_file.endswith(".vxa"):
            print dna_file

            tree = ET.ElementTree(file= os.path.join(path, dna_file))
            root = tree.getroot()
            layers = root.find('VXC').find('Structure').find('Data').findall('Layer')

            """Calculates probability based on amount of fat tissue
            """
            dna = ""
            for layer in layers:
                dna += str(layer.text).strip()
            count_soft = dna.count('1')
            probability = (count_soft / 1000) * 0.5 # or 0.0005 * count_soft

            dna_list = ""
            for layer in layers:
                dna_list = list(layer.text.strip())
                position_to_check = 0
                for index in range(len(dna_list)):
                    tissue = dna_list[index]
                    if tissue == '3' or tissue == '4':
                        if random.random() <= probability:
                            dna_list[index] = '2'

                layer.text = "".join(dna_list)
                tree.write(os.path.join(path, dna_file))

atropyMuscles(sys.argv[1])
