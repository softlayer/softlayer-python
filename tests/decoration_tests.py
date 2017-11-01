"""
    SoftLayer.tests.decoration_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""

from SoftLayer.decoration import retry
from SoftLayer import exceptions
from SoftLayer import testing
import unittest


class TestDecoration(testing.TestCase):

    def test_no_retry_required(self):
        self.counter = 0

        @retry(exceptions.SoftLayerError, tries=4, delay=0.1)
        def succeeds():
            self.counter += 1
            return 'success'

        r = succeeds()

        self.assertEqual(r, 'success')
        self.assertEqual(self.counter, 1)

    def test_retries_once(self):
        self.counter = 0

        @retry(exceptions.SoftLayerError, tries=4, delay=0.1)
        def fails_once():
            self.counter += 1
            if self.counter < 2:
                raise exceptions.SoftLayerError('failed')
            else:
                return 'success'

        r = fails_once()
        self.assertEqual(r, 'success')
        self.assertEqual(self.counter, 2)

    def test_limit_is_reached(self):
        self.counter = 0

        @retry(exceptions.SoftLayerError, tries=4, delay=0.1)
        def always_fails():
            self.counter += 1
            raise exceptions.SoftLayerError('failed')

        self.assertRaises(exceptions.SoftLayerError, always_fails)
        self.assertEqual(self.counter, 4)

    def test_multiple_exception_types(self):
        self.counter = 0

        @retry((exceptions.SoftLayerError, TypeError), tries=4, delay=0.1)
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

        @retry(exceptions.SoftLayerError, tries=4, delay=0.1)
        def raise_unexpected_error():
            raise TypeError('unexpected error')

        self.assertRaises(TypeError, raise_unexpected_error)


if __name__ == '__main__':

    unittest.main()
