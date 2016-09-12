#!/usr/bin/env python
# -*- coding: utf-8 -*-
# see python document 26.3.5.
import unittest
import doctest
import WaitQueue


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(WaitQueue))
    return tests
