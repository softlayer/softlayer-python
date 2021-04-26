"""
    SoftLayer.tests.managers.vs.vs_waiting_for_ready_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.

"""
from unittest import mock as mock

import SoftLayer
from SoftLayer import exceptions
from SoftLayer import testing


class VSWaitReadyGoTests(testing.TestCase):

    def set_up(self):
        self.client = mock.MagicMock()
        self.vs = SoftLayer.VSManager(self.client)
        self.guestObject = self.client['Virtual_Guest'].getObject

    @mock.patch('SoftLayer.managers.vs.VSManager.wait_for_ready')
    def test_wait_interface(self, ready):
        # verify interface to wait_for_ready is intact
        self.vs.wait_for_transaction(1, 1)
        ready.assert_called_once_with(1, 1, delay=10, pending=True)

    def test_active_not_provisioned(self):
        # active transaction and no provision date should be false
        self.guestObject.return_value = {'activeTransaction': {'id': 1}}
        value = self.vs.wait_for_ready(1, 0)
        self.assertFalse(value)

    def test_active_and_provisiondate(self):
        # active transaction and provision date should be True
        self.guestObject.side_effect = [
            {'activeTransaction': {'id': 1},
             'provisionDate': 'aaa'},
        ]
        value = self.vs.wait_for_ready(1, 1)
        self.assertTrue(value)

    @mock.patch('time.sleep')
    @mock.patch('time.time')
    def test_active_provision_pending(self, _now, _sleep):
        _now.side_effect = [0, 0, 1, 1, 2, 2]
        # active transaction and provision date
        # and pending should be false
        self.guestObject.return_value = {'activeTransaction': {'id': 2}, 'provisionDate': 'aaa'}

        value = self.vs.wait_for_ready(instance_id=1, limit=1, delay=1, pending=True)
        _sleep.assert_has_calls([mock.call(0)])
        self.assertFalse(value)

    def test_reload_no_pending(self):
        # reload complete, maintance transactions
        self.guestObject.return_value = {
            'activeTransaction': {'id': 2},
            'provisionDate': 'aaa',
            'lastOperatingSystemReload': {'id': 1},
        }

        value = self.vs.wait_for_ready(1, 1)
        self.assertTrue(value)

    @mock.patch('time.sleep')
    @mock.patch('time.time')
    def test_reload_pending(self, _now, _sleep):
        _now.side_effect = [0, 0, 1, 1, 2, 2]
        # reload complete, pending maintance transactions
        self.guestObject.return_value = {'activeTransaction': {'id': 2},
                                         'provisionDate': 'aaa',
                                         'lastOperatingSystemReload': {'id': 1}}
        value = self.vs.wait_for_ready(instance_id=1, limit=1, delay=1, pending=True)
        _sleep.assert_has_calls([mock.call(0)])
        self.assertFalse(value)

    @mock.patch('time.sleep')
    def test_ready_iter_once_incomplete(self, _sleep):
        # no iteration, false
        self.guestObject.return_value = {'activeTransaction': {'id': 1}}
        value = self.vs.wait_for_ready(1, 0, delay=1)
        self.assertFalse(value)
        _sleep.assert_has_calls([mock.call(0)])

    @mock.patch('time.sleep')
    def test_iter_once_complete(self, _sleep):
        # no iteration, true
        self.guestObject.return_value = {'provisionDate': 'aaa'}
        value = self.vs.wait_for_ready(1, 1, delay=1)
        self.assertTrue(value)
        self.assertFalse(_sleep.called)

    @mock.patch('time.sleep')
    def test_iter_four_complete(self, _sleep):
        # test 4 iterations with positive match
        self.guestObject.side_effect = [
            {'activeTransaction': {'id': 1}},
            {'activeTransaction': {'id': 1}},
            {'activeTransaction': {'id': 1}},
            {'provisionDate': 'aaa'},
        ]

        value = self.vs.wait_for_ready(1, 4, delay=1)
        self.assertTrue(value)
        _sleep.assert_has_calls([mock.call(1), mock.call(1), mock.call(1)])
        self.guestObject.assert_has_calls([
            mock.call(id=1, mask=mock.ANY), mock.call(id=1, mask=mock.ANY),
            mock.call(id=1, mask=mock.ANY), mock.call(id=1, mask=mock.ANY),
        ])

    @mock.patch('time.time')
    @mock.patch('time.sleep')
    def test_iter_two_incomplete(self, _sleep, _time):
        # test 2 iterations, with no matches
        self.guestObject.side_effect = [
            {'activeTransaction': {'id': 1}},
            {'activeTransaction': {'id': 1}},
            {'activeTransaction': {'id': 1}},
            {'provisionDate': 'aaa'}
        ]
        # logging calls time.time as of pytest3.3, not sure if there is a better way of getting around that.
        _time.side_effect = [0, 1, 2, 3, 4, 5, 6]
        value = self.vs.wait_for_ready(1, 2, delay=1)
        self.assertFalse(value)
        _sleep.assert_has_calls([mock.call(1), mock.call(0)])
        self.guestObject.assert_has_calls([
            mock.call(id=1, mask=mock.ANY),
            mock.call(id=1, mask=mock.ANY),
        ])

    @mock.patch('time.time')
    @mock.patch('time.sleep')
    def test_iter_20_incomplete(self, _sleep, _time):
        """Wait for up to 20 seconds (sleeping for 10 seconds) for a server."""
        self.guestObject.return_value = {'activeTransaction': {'id': 1}}
        # logging calls time.time as of pytest3.3, not sure if there is a better way of getting around that.
        _time.side_effect = [0, 0, 10, 10, 20, 20, 50, 60]
        value = self.vs.wait_for_ready(1, 20, delay=10)
        self.assertFalse(value)
        self.guestObject.assert_has_calls([mock.call(id=1, mask=mock.ANY)])

        _sleep.assert_has_calls([mock.call(10)])

    @mock.patch('SoftLayer.decoration.sleep')
    @mock.patch('SoftLayer.transports.FixtureTransport.__call__')
    @mock.patch('time.time')
    @mock.patch('time.sleep')
    def test_exception_from_api(self, _sleep, _time, _vs, _dsleep):
        """Tests escalating scale back when an excaption is thrown"""
        _dsleep.return_value = False

        self.guestObject.side_effect = [
            exceptions.ServerError(504, "Its broken"),
            {'activeTransaction': {'id': 1}},
            {'provisionDate': 'aaa'}
        ]
        # logging calls time.time as of pytest3.3, not sure if there is a better way of getting around that.
        _time.side_effect = [0, 1, 2, 3, 4]
        value = self.vs.wait_for_ready(1, 20, delay=1)
        _sleep.assert_called_once()
        _dsleep.assert_called_once()
        self.assertTrue(value)
