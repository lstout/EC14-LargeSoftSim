import os
from FeatureExtractorAbstract import FeatureExtractorAbstract
from ..helpers.pathConfig import PathConfig
from ..helpers.voxelData import VoxelData
from ..helpers.utilities import get_before_after_vox, get_config_attr
from ..helpers import disease_functions as disease

class Disease(FeatureExtractorAbstract):
    def getCSVheader(self):
        return ['DiseaseType', 'DiseaseStrength', 'probability']

    def extract(self, args):
        if args['exp_type'] == 'no disease':
            vd = args['voxelBefore']
        else:
            vd = args['voxelAfter']
        dnaMatrix = vd.getDNAmatrix().astype(int)
        if type(dnaMatrix) == bool and not dnaMatrix:
            return ['NA'] * 3
        try:
            cell_fn_name = args['config'].get("Disease", "cell_function")
            indiv_fn_name = args['config'].get("Disease", "indiv_function")        
        except Exception as e:
            print type(e), e
            return ['NA'] * 3
        try:
            cell_fn = getattr(disease, cell_fn_name)
            prob = cell_fn(dnaMatrix)
            return [indiv_fn_name, cell_fn_name, prob]
        except AttributeError as e:
            return ['NA'] * 3
