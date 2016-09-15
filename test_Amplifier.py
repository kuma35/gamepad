#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import Amplifier


class Testmplify(unittest.TestCase):
    """ Checking input value to step angle. """

    def test_amplify_input_to_step_angle(self):
        """Inputing value is -1.0 to 1.0 step 0.1. """
        amp = Amplifier.Amplifier()
        for sens in [-1.0, -0.9, -0.8, -0.7]:
            with self.subTest(msg='-1.0 to -0.7', sens=sens):
                (step, speed) = amp.get_angle(sens)
                self.assertEqual(step, -2)
        for sens in [-0.6, -0.5, -0.4, -0.3]:
            with self.subTest(msg='-0.6 to -0.3', sens=sens):
                (step, speed) = amp.get_angle(sens)
                self.assertEqual(step, -1)
        for sens in [-0.2, -0.1, 0.0, 0.1, 0.2]:
            with self.subTest(msg='-0.2 to 0.2', sens=sens):
                (step, speed) = amp.get_angle(sens)
                self.assertEqual(step, 0)
        for sens in [0.3, 0.4, 0.5, 0.6]:
            with self.subTest(msg='0.3 to 0.6', sens=sens):
                (step, speed) = amp.get_angle(sens)
                self.assertEqual(step, 1)
        for sens in [0.7, 0.8, 0.9, 1.0]:
            with self.subTest(msg='0.7 to 1.0', sens=sens):
                (step, speed) = amp.get_angle(sens)
                self.assertEqual(step, 2)


    def test_outrange_values(self):
        """Inputing value is out of ranges. """
        amp = Amplifier.Amplifier()
        for sens in [-1.1, -5, -100]:
            with self.subTest(msg='-1.1, -5, -100', sens=sens):
                (step, speed) = amp.get_angle(sens)
                self.assertEqual(step, -2)

        for sens in [1.1, 5, 100]:
            with self.subTest(msg='1.1, 5, 100', sens=sens):
                (step, speed) = amp.get_angle(sens)
                self.assertEqual(step, 2)


class TestBeamAmplify(unittest.TestCase):
    """ Checking input value to step angle. """
    def test_amplify_input_to_step_angle(self):
        """Inputing value is -1.0 to 1.0 step 0.1. """
        amp = Amplifier.BeamAmplifier()
        for sens in [-1.0, -0.9, -0.8, -0.7]:
            with self.subTest(msg='-1.0 to -0.7', sens=sens):
                (step, speed) = amp.get_angle(sens)
                self.assertEqual(step, -100)
        for sens in [-0.6, -0.5, -0.4, -0.3]:
            with self.subTest(msg='-0.6 to -0.3', sens=sens):
                (step, speed) = amp.get_angle(sens)
                self.assertEqual(step, -50)
        for sens in [-0.2, -0.1, 0.0, 0.1, 0.2]:
            with self.subTest(msg='-0.2 to 0.2', sens=sens):
                (step, speed) = amp.get_angle(sens)
                self.assertEqual(step, 0)
        for sens in [0.3, 0.4, 0.5, 0.6]:
            with self.subTest(msg='0.3 to 0.6', sens=sens):
                (step, speed) = amp.get_angle(sens)
                self.assertEqual(step, 50)
        for sens in [0.7, 0.8, 0.9, 1.0]:
            with self.subTest(msg='0.7 to 1.0', sens=sens):
                (step, speed) = amp.get_angle(sens)
                self.assertEqual(step, 100)

    def test_outrange_values(self):
        """Inputing value is out of ranges. """
        amp = Amplifier.BeamAmplifier()
        for sens in [-1.1, -5, -100]:
            with self.subTest(msg='-1.1, -5, -100', sens=sens):
                (step, speed) = amp.get_angle(sens)
                self.assertEqual(step, -100)

        for sens in [1.1, 5, 100]:
            with self.subTest(msg='1.1, 5, 100', sens=sens):
                (step, speed) = amp.get_angle(sens)
                self.assertEqual(step, 100)


class TestArmAmplify(unittest.TestCase):
    """ Checking input value to step angle. """
    def test_amplify_input_to_step_angle(self):
        """Inputing value is -1.0 to 1.0 step 0.1. """
        amp = Amplifier.ArmAmplifier()
        for sens in [-1.0, -0.9, -0.8, -0.7]:
            with self.subTest(msg='-1.0 to -0.7', sens=sens):
                (step, speed) = amp.get_angle(sens)
                self.assertEqual(step, -100)
        for sens in [-0.6, -0.5, -0.4, -0.3]:
            with self.subTest(msg='-0.6 to -0.3', sens=sens):
                (step, speed) = amp.get_angle(sens)
                self.assertEqual(step, -50)
        for sens in [-0.2, -0.1, 0.0, 0.1, 0.2]:
            with self.subTest(msg='-0.2 to 0.2', sens=sens):
                (step, speed) = amp.get_angle(sens)
                self.assertEqual(step, 0)
        for sens in [0.3, 0.4, 0.5, 0.6]:
            with self.subTest(msg='0.3 to 0.6', sens=sens):
                (step, speed) = amp.get_angle(sens)
                self.assertEqual(step, 50)
        for sens in [0.7, 0.8, 0.9, 1.0]:
            with self.subTest(msg='0.7 to 1.0', sens=sens):
                (step, speed) = amp.get_angle(sens)
                self.assertEqual(step, 100)

    def test_outrange_values(self):
        """Inputing value is out of ranges. """
        amp = Amplifier.ArmAmplifier()
        for sens in [-1.1, -5, -100]:
            with self.subTest(msg='-1.1, -5, -100', sens=sens):
                (step, speed) = amp.get_angle(sens)
                self.assertEqual(step, -100)

        for sens in [1.1, 5, 100]:
            with self.subTest(msg='1.1, 5, 100', sens=sens):
                (step, speed) = amp.get_angle(sens)
                self.assertEqual(step, 100)
