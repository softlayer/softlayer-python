"""
    SoftLayer.tests.decoration_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""

import logging
import mock

from SoftLayer.decoration import retry
from SoftLayer import exceptions
from SoftLayer import testing


class TestDecoration(testing.TestCase):

    def setUp(self):
        super(TestDecoration, self).setUp()
        self.patcher = mock.patch('SoftLayer.decoration.sleep')
        self.patcher.return_value = False
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.counter = 0

    def test_no_retry_required(self):

        @retry(exceptions.SoftLayerError, tries=4)
        def succeeds():
            self.counter += 1
            return 'success'

        r = succeeds()

        self.assertEqual(r, 'success')
        self.assertEqual(self.counter, 1)

    @mock.patch('SoftLayer.decoration.randint')
    def test_retries_once(self, _random):

        _random.side_effect = [0, 0, 0, 0]

        @retry(exceptions.SoftLayerError, tries=4, logger=logging.getLogger(__name__))
        def fails_once():
            self.counter += 1
            if self.counter < 2:
                raise exceptions.SoftLayerError('failed')
            else:
                return 'success'

        with self.assertLogs(__name__, level='WARNING') as log:
            r = fails_once()

        self.assertEqual(log.output, ["WARNING:tests.decoration_tests:failed, Retrying in 5 seconds..."])
        self.assertEqual(r, 'success')
        self.assertEqual(self.counter, 2)

    def test_limit_is_reached(self):

        @retry(exceptions.SoftLayerError, tries=4)
        def always_fails():
            self.counter += 1
            raise exceptions.SoftLayerError('failed!')

        self.assertRaises(exceptions.SoftLayerError, always_fails)
        self.assertEqual(self.counter, 4)

    def test_multiple_exception_types(self):

        @retry((exceptions.SoftLayerError, TypeError), tries=4)
        def raise_multiple_exceptions():
            self.counter += 1
            if self.counter == 1:
                raise exceptions.SoftLayerError('a retryable error')
            elif self.counter == 2:
                raise TypeError('another retryable error')
            else:
                return 'success'

        r = raise_multiple_exceptions()
        self.assertEqual(r, 'success')
        self.assertEqual(self.counter, 3)

    def test_unexpected_exception_does_not_retry(self):

        @retry(exceptions.SoftLayerError, tries=4)
        def raise_unexpected_error():
            raise TypeError('unexpected error')

        self.assertRaises(TypeError, raise_unexpected_error)
