from FeatureExtractorAbstract import FeatureExtractorAbstract


class BasicInfo(FeatureExtractorAbstract):
    def getCSVheader(self):
        return ['Ind_ID', 'Exp_Num', 'Exp_type', 'Arena_Size', 'Arena_size_x', 'Arena_size_y']

    def extract(self, experiment, type, indiv, arena_size):
        if type == "no disease":
            t = "nd"
        else:
            t = "wd"

        return [indiv[0], experiment[0], t, arena_size['name'], arena_size['x'], arena_size['y']]
