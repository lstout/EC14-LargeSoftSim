import numpy as np
import os
from FeatureExtractorAbstract import FeatureExtractorAbstract
from ..helpers.pathConfig import PathConfig
from ..helpers.distanceCalc import DistanceCalc
from ..helpers.utilities import get_before_after_trace


class Gait(FeatureExtractorAbstract):
    def __init__(self):
        self.dc = DistanceCalc()

    def getCSVheader(self):
        return ["gaitPeriodX", "gaitErrorX", "gaitPeriodY", "gaitErrorY", "gaitPeriodZ", "gaitErrorZ"]

    def extract(self, args):
        if args['exp_type'] == 'no disease':
            traces = args['tracesBefore']
        else:
            traces = args['tracesAfter']

        if traces == []:
            return ['NA'] * 6

        xPeriod, xError = self.getPeriod(traces[1,:])
        yPeriod, yError = self.getPeriod(traces[2,:])
        zPeriod, zError = self.getPeriod(traces[3,:])
	return [xPeriod, xError, yPeriod, yError, zPeriod, zError]

    def getPeriod(self, signal):
        if len(signal) in [0,1]:
            return 'NA', 'NA'
        fft = np.fft.rfft(signal).real
        fft = fft[:len(fft) / 2 + 1]
        fft[1:] = fft[1:] / (len(signal)/2)
        fft[0] = fft[0]/len(signal)

        period = np.argmax(fft[1:]) + 1
        period_value = fft[1:].max()
      
        linspace = np.linspace(0,len(signal), len(signal))
        mse = np.average(signal - (period_value * np.sin(period*linspace+np.average(signal)))**2)
        return period, mse
