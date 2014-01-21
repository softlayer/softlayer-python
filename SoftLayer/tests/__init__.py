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

__all__ = ['unittest', 'FixtureClient']
