# -*- coding:utf-8 mode:Python -*-
from logging import getLogger, NullHandler, DEBUG


class Amplifier(object):
    """Amplify input-value to step-angle.
    Input value is -1.0 to 1.0.
    0.0 is center.
    'stay' is center value range.
    'walk' is slow move.
    'trot' is move (over walk).
    """
    def __init__(self, logger=None):
        self.sensitive = {
            'stay':0.3,
            'walk':0.6,
            'trot':1.0,
        }
        self.angle = {
            'stay':0,
            'walk':1,
            'trot':2,
        }
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
        sign = 1;
        if sense < 0:
            sign = -1;
        if abs(sense) < self.sensitive['stay']:
            return self.angle['stay'] * sign
        elif abs(sense) < self.sensitive['walk']:
            return self.angle['walk'] * sign
        else:
            return self.angle['trot'] * sign


class BeamAmplifier(Amplifier):
    """ for beam input to beam servo
    Input value is -1.0 to 1.0.
    0.0 is center.
    'stay' is center value range.
    'walk' is slow move.
    'trot' is move (over walk).
    """
    def __init__(self, logger=None):
        super(BeamAmplifier, self).__init__(logger)
        self.sensitive = {
            'stay':0.3,
            'walk':0.6,
            'trot':1.0,
        }
        self.angle = {
            'stay':0,
            'walk':5,
            'trot':10,
        }
