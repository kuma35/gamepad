# -*- coding:utf-8 mode:Python -*-
from logging import getLogger, NullHandler, DEBUG


class Amplifier(object):
    """Amplify input-value to step-angle.
    Input value is -1.0 to 1.0.
    0.0 is center.
    Converting table is self.cnv
    sens < self.cnv[x]['sep']
    """
    def __init__(self, logger=None):
        self.cnv = [{'sep':-0.6, 'step':-2, 'speed':10,},
                    {'sep':-0.2, 'step':-1, 'speed':10,},
                    {'sep':0.3, 'step':0, 'speed':0,},
                    {'sep':0.7, 'step':1, 'speed':10,},]
        self.cnv_last = {'step':2, 'speed':10,}
        if logger is None:
            self.logger = getLogger(__name__)
            sh = NullHandler()
            sh.setLevel(DEBUG)
            self.logger.setLevel(DEBUG)
            self.logger.addHandler(sh)
        else:
            self.logger = logger

    def get_angle(self, sense):
        """
        sense value: -1.0 to 1.0
        """
        for x in self.cnv:
            if sense < x['sep']:
                return (x['step'], x['speed'])
        return (self.cnv_last['step'], self.cnv_last['speed'])


class BeamAmplifier(Amplifier):
    """ for beam input to beam servo
    Input value is -1.0 to 1.0.
    0.0 is center.
    """
    def __init__(self, logger=None):
        super(BeamAmplifier, self).__init__(logger)
        self.cnv = [{'sep':-0.6, 'step':-100, 'speed':10,},
                    {'sep':-0.2, 'step':-50, 'speed':10,},
                    {'sep':0.3, 'step':0, 'speed':0,},
                    {'sep':0.7, 'step':50, 'speed':10,},]
        self.cnv_last = {'step':100, 'speed':10,}


class ArmAmplifier(Amplifier):
    """ for beam input to armservo
    Input value is -1.0 to 1.0.
    0.0 is center.
    """
    def __init__(self, logger=None):
        super(ArmAmplifier, self).__init__(logger)
        self.cnv = [{'sep':-0.6, 'step':-100, 'speed':10,},
                    {'sep':-0.2, 'step':-50, 'speed':10,},
                    {'sep':0.3, 'step':0, 'speed':0,},
                    {'sep':0.7, 'step':50, 'speed':10,},]
        self.cnv_last = {'step':100, 'speed':10,}
