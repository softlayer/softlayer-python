
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA
import os.path

FIXTURE_PATH = os.path.abspath(os.path.join(__file__, '..', 'fixtures'))
