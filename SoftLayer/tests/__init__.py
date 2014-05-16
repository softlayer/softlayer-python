"""
    SoftLayer.tests
    ~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
try:
    import unittest2 as unittest
except ImportError:
    import unittest
import os.path

from .fixture_client import FixtureClient

FIXTURE_PATH = os.path.abspath(os.path.join(__file__, '..', 'fixtures'))


class TestCase(unittest.TestCase):
    def set_up(self):
        pass

    def tear_down(self):
        pass

    def setUp(self):  # NOQA
        return self.set_up()

    def tearDown(self):  # NOQA
        return self.tear_down()

__all__ = ['unittest', 'FixtureClient']
