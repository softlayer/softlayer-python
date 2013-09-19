"""
    SoftLayer.tests
    ~~~~~~~~~~~~~~~

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: MIT, see LICENSE for more details.
"""
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA
import os.path

FIXTURE_PATH = os.path.abspath(os.path.join(__file__, '..', 'fixtures'))
