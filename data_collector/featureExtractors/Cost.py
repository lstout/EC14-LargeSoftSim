import os
from FeatureExtractorAbstract import FeatureExtractorAbstract
from ..helpers.utilities import get_config_attr

class Cost(FeatureExtractorAbstract):
    def getCSVheader(self):
        return ['muscleCost', 'fatCost']

    def extract(self, args):
        muscle_cost = args['config'].getfloat("Lifetimes", "cost_muscle")
        fat_cost = args['config'].getfloat("Lifetimes", "cost_soft")
        return [muscle_cost, fat_cost]
