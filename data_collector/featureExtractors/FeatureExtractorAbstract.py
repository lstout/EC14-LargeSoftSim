class FeatureExtractorAbstract(object):
    """ Template class for feature extractors
    """

    def getCSVheader(self):
        """ get CSV column headers for this FE

        :return: List of column headers (strings) for the CSV file for this FE
        """
        raise NotImplementedError("FeatureExtractor %s doesn't implement getCSVheader()" % (self.__class__.__name__))

    def extract(self, args):
        """ Does the actual extraction of one or multiple features

        :param args: a dictionary with all info on the experiment/individual
        :return: list of feature values
        """
        raise NotImplementedError("FeatureExtractor %s doesn't implement extract()" % (self.__class__.__name__))
