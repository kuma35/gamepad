#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import Amplifier


class TestBeamAmplify(unittest.TestCase):
    """ Checking input value to step angle. """

    def test_amplify_beam_input_to_step_angle(self):
        """Inputing value is -1.0 to 1.0 step 0.1. """
        beam_amp = Amplifier.BeamAmplifier()
        for sens_x10 in range(0, -3, -1):
            sens = sens_x10 / 10
            with self.subTest(msg='0.0 to -0.2', sens=sens):
                self.assertEqual(beam_amp.get_angle(sens), 0)
        for sens_x10 in range(-3, -6, -1):
            sens = sens_x10 / 10
            with self.subTest(msg='-0.3 to -0.5', sens=sens):
                self.assertEqual(beam_amp.get_angle(sens), -5)
        for sens_x10 in range(-6, -11, -1):
            sens = sens_x10 / 10
            with self.subTest(msg='-0.6 to -1.0', sens=sens):
                self.assertEqual(beam_amp.get_angle(sens), -10)
        for sens_x10 in range(0, 3):
            sens = sens_x10 / 10
            with self.subTest(msg='0.0 to 0.2', sens=sens):
                self.assertEqual(beam_amp.get_angle(sens), 0)
        for sens_x10 in range(3, 6):
            sens = sens_x10 / 10
            with self.subTest(msg='0.3 to 0.5', sens=sens):
                self.assertEqual(beam_amp.get_angle(sens), 5)
        for sens_x10 in range(6, 11):
            sens = sens_x10 / 10
            with self.subTest(msg='0.6 to 1.0', sens=sens):
                self.assertEqual(beam_amp.get_angle(sens), 10)

    def test_outrange_values(self):
        """Inputing value is out of ranges. """
        beam_amp = Amplifier.BeamAmplifier()
        for sens in [-1.1, -5, -100]:
            with self.subTest(msg='-1.1, -5, -100', sens=sens):
                self.assertEqual(beam_amp.get_angle(sens), -10)
        for sens in [1.1, 5, 100]:
            with self.subTest(msg='1.1, 5, 100', sens=sens):
                self.assertEqual(beam_amp.get_angle(sens), 10)
