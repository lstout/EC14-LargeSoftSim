from FeatureExtractorAbstract import FeatureExtractorAbstract


class BasicInfo(FeatureExtractorAbstract):
    def getCSVheader(self):
        return ['Ind_ID', 'Exp_Num', 'Exp_type', 'Arena_Size', 'Arena_size_x', 'Arena_size_y']

    def extract(self, args):
        return [args['indiv'][0], args['exp'][0], args['exp_type'],
                args['arena_size']['name'], args['arena_size']['x'], args['arena_size']['y']]
