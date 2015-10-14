"""
    SoftLayer.tests.managers.queue_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import mock

import SoftLayer
from SoftLayer import consts
from SoftLayer.managers import messaging
from SoftLayer import testing

QUEUE_1 = {
    'expiration': 40000,
    'message_count': 0,
    'name': 'example_queue',
    'tags': ['tag1', 'tag2', 'tag3'],
    'visibility_interval': 10,
    'visible_message_count': 0}
QUEUE_LIST = {'item_count': 1, 'items': [QUEUE_1]}
MESSAGE_1 = {
    'body': '<body>',
    'fields': {'field': 'value'},
    'id': 'd344a01133b61181f57d9950a852eb10',
    'initial_entry_time': 1343402631.3917992,
    'message': 'Object created',
    'visibility_delay': 0,
    'visibility_interval': 30000}
MESSAGE_POP = {
    'item_count': 1,
    'items': [MESSAGE_1],
}
MESSAGE_POP_EMPTY = {
    'item_count': 0,
    'items': []
}

TOPIC_1 = {'name': 'example_topic', 'tags': ['tag1', 'tag2', 'tag3']}
TOPIC_LIST = {'item_count': 1, 'items': [TOPIC_1]}
SUBSCRIPTION_1 = {
    'endpoint': {
        'account_id': 'test',
        'queue_name': 'topic_subscription_queue'},
    'endpoint_type': 'queue',
    'id': 'd344a01133b61181f57d9950a85704d4',
    'message': 'Object created'}
SUBSCRIPTION_LIST = {'item_count': 1, 'items': [SUBSCRIPTION_1]}


def mocked_auth_call(self):
    self.auth_token = 'NEW_AUTH_TOKEN'


class QueueAuthTests(testing.TestCase):
    def set_up(self):
        self.auth = messaging.QueueAuth(
            'endpoint', 'username', 'api_key', auth_token='auth_token')

    def test_init(self):
        auth = SoftLayer.managers.messaging.QueueAuth(
            'endpoint', 'username', 'api_key', auth_token='auth_token')
        self.assertEqual(auth.endpoint, 'endpoint')
        self.assertEqual(auth.username, 'username')
        self.assertEqual(auth.api_key, 'api_key')
        self.assertEqual(auth.auth_token, 'auth_token')

    @mock.patch('SoftLayer.managers.messaging.requests.post')
    def test_auth(self, post):
        post().headers = {'X-Auth-Token': 'NEW_AUTH_TOKEN'}
        post().ok = True
        self.auth.auth()
        self.auth.auth_token = 'NEW_AUTH_TOKEN'

        post().ok = False
        self.assertRaises(SoftLayer.Unauthenticated, self.auth.auth)

    @mock.patch('SoftLayer.managers.messaging.QueueAuth.auth',
                mocked_auth_call)
    def test_handle_error_200(self):
        # No op on no error
        request = mock.MagicMock()
        request.status_code = 200
        self.auth.handle_error(request)

        self.assertEqual(self.auth.auth_token, 'auth_token')
        self.assertFalse(request.request.send.called)

    @mock.patch('SoftLayer.managers.messaging.QueueAuth.auth',
                mocked_auth_call)
    def test_handle_error_503(self):
        # Retry once more on 503 error
        request = mock.MagicMock()
        request.status_code = 503
        self.auth.handle_error(request)

        self.assertEqual(self.auth.auth_token, 'auth_token')
        request.connection.send.assert_called_with(request.request)

    @mock.patch('SoftLayer.managers.messaging.QueueAuth.auth',
                mocked_auth_call)
    def test_handle_error_401(self):
        # Re-auth on 401
        request = mock.MagicMock()
        request.status_code = 401
        request.request.headers = {'X-Auth-Token': 'OLD_AUTH_TOKEN'}
        self.auth.handle_error(request)

        self.assertEqual(self.auth.auth_token, 'NEW_AUTH_TOKEN')
        request.connection.send.assert_called_with(request.request)

    @mock.patch('SoftLayer.managers.messaging.QueueAuth.auth',
                mocked_auth_call)
    def test_call_unauthed(self):
        request = mock.MagicMock()
        request.headers = {}
        self.auth.auth_token = None
        self.auth(request)

        self.assertEqual(self.auth.auth_token, 'NEW_AUTH_TOKEN')
        request.register_hook.assert_called_with(
            'response', self.auth.handle_error)
        self.assertEqual(request.headers, {'X-Auth-Token': 'NEW_AUTH_TOKEN'})


class MessagingManagerTests(testing.TestCase):

    def set_up(self):
        self.client = mock.MagicMock()
        self.manager = SoftLayer.MessagingManager(self.client)

    def test_list_accounts(self):
        self.manager.list_accounts()
        self.client['Account'].getMessageQueueAccounts.assert_called_with(
            mask=mock.ANY)

    def test_get_endpoints(self):
        endpoints = self.manager.get_endpoints()
        self.assertEqual(endpoints, SoftLayer.managers.messaging.ENDPOINTS)

    @mock.patch('SoftLayer.managers.messaging.ENDPOINTS', {
        'datacenter01': {
            'private': 'private_endpoint', 'public': 'public_endpoint'},
        'dal05': {
            'private': 'dal05_private', 'public': 'dal05_public'}})
    def test_get_endpoint(self):
        # Defaults to dal05, public
        endpoint = self.manager.get_endpoint()
        self.assertEqual(endpoint, 'https://dal05_public')

        endpoint = self.manager.get_endpoint(network='private')
        self.assertEqual(endpoint, 'https://dal05_private')

        endpoint = self.manager.get_endpoint(datacenter='datacenter01')
        self.assertEqual(endpoint, 'https://public_endpoint')

        endpoint = self.manager.get_endpoint(datacenter='datacenter01',
                                             network='private')
        self.assertEqual(endpoint, 'https://private_endpoint')

        endpoint = self.manager.get_endpoint(datacenter='datacenter01',
                                             network='private')
        self.assertEqual(endpoint, 'https://private_endpoint')

        # ERROR CASES
        self.assertRaises(
            TypeError,
            self.manager.get_endpoint, datacenter='doesnotexist')

        self.assertRaises(
            TypeError,
            self.manager.get_endpoint, network='doesnotexist')

    @mock.patch('SoftLayer.managers.messaging.MessagingConnection')
    def test_get_connection(self, conn):
        queue_conn = self.manager.get_connection('QUEUE_ACCOUNT_ID')
        conn.assert_called_with(
            'QUEUE_ACCOUNT_ID', endpoint='https://dal05.mq.softlayer.net')
        conn().authenticate.assert_called_with(
            self.client.auth.username, self.client.auth.api_key)
        self.assertEqual(queue_conn, conn())

    def test_get_connection_no_auth(self):
        self.client.auth = None
        self.assertRaises(SoftLayer.SoftLayerError,
                          self.manager.get_connection, 'QUEUE_ACCOUNT_ID')

    def test_get_connection_no_username(self):
        self.client.auth.username = None
        self.assertRaises(SoftLayer.SoftLayerError,
                          self.manager.get_connection, 'QUEUE_ACCOUNT_ID')

    def test_get_connection_no_api_key(self):
        self.client.auth.api_key = None
        self.assertRaises(SoftLayer.SoftLayerError,
                          self.manager.get_connection, 'QUEUE_ACCOUNT_ID')

    @mock.patch('SoftLayer.managers.messaging.requests.get')
    def test_ping(self, get):
        result = self.manager.ping()

        get.assert_called_with('https://dal05.mq.softlayer.net/v1/ping')
        get().raise_for_status.assert_called_with()
        self.assertTrue(result)


class MessagingConnectionTests(testing.TestCase):

    def set_up(self):
        self.conn = SoftLayer.managers.messaging.MessagingConnection(
            'acount_id', endpoint='endpoint')
        self.auth = mock.MagicMock()
        self.conn.auth = self.auth

    def test_init(self):
        self.assertEqual(self.conn.account_id, 'acount_id')
        self.assertEqual(self.conn.endpoint, 'endpoint')
        self.assertEqual(self.conn.auth, self.auth)

    @mock.patch('SoftLayer.managers.messaging.requests.request')
    def test_make_request(self, request):
        resp = self.conn._make_request('GET', 'path')
        request.assert_called_with(
            'GET', 'endpoint/v1/acount_id/path',
            headers={
                'Content-Type': 'application/json',
                'User-Agent': consts.USER_AGENT},
            auth=self.auth)
        request().raise_for_status.assert_called_with()
        self.assertEqual(resp, request())

    @mock.patch('SoftLayer.managers.messaging.QueueAuth')
    def test_authenticate(self, auth):
        self.conn.authenticate('username', 'api_key', auth_token='auth_token')

        auth.assert_called_with(
            'endpoint/v1/acount_id/auth', 'username', 'api_key',
            auth_token='auth_token')
        auth().auth.assert_called_with()
        self.assertEqual(self.conn.auth, auth())

    @mock.patch('SoftLayer.managers.messaging.MessagingConnection'
                '._make_request')
    def test_stats(self, make_request):
        content = {
            'notifications': [{'key': [2012, 7, 27, 14, 31], 'value': 2}],
            'requests': [{'key': [2012, 7, 27, 14, 31], 'value': 11}]}
        make_request().json.return_value = content
        result = self.conn.stats()

        make_request.assert_called_with('get', 'stats/hour')
        self.assertEqual(content, result)

    # Queue-based Tests
    @mock.patch('SoftLayer.managers.messaging.MessagingConnection'
                '._make_request')
    def test_get_queues(self, make_request):
        make_request().json.return_value = QUEUE_LIST
        result = self.conn.get_queues()

        make_request.assert_called_with('get', 'queues', params={})
        self.assertEqual(QUEUE_LIST, result)

        # with tags
        result = self.conn.get_queues(tags=['tag1', 'tag2'])

        make_request.assert_called_with(
            'get', 'queues', params={'tags': 'tag1,tag2'})
        self.assertEqual(QUEUE_LIST, result)

    @mock.patch('SoftLayer.managers.messaging.MessagingConnection'
                '._make_request')
    def test_create_queue(self, make_request):
        make_request().json.return_value = QUEUE_1
        result = self.conn.create_queue('example_queue')

        make_request.assert_called_with(
            'put', 'queues/example_queue', data='{}')
        self.assertEqual(QUEUE_1, result)

    @mock.patch('SoftLayer.managers.messaging.MessagingConnection'
                '._make_request')
    def test_modify_queue(self, make_request):
        make_request().json.return_value = QUEUE_1
        result = self.conn.modify_queue('example_queue')

        make_request.assert_called_with(
            'put', 'queues/example_queue', data='{}')
        self.assertEqual(QUEUE_1, result)

    @mock.patch('SoftLayer.managers.messaging.MessagingConnection'
                '._make_request')
    def test_get_queue(self, make_request):
        make_request().json.return_value = QUEUE_1
        result = self.conn.get_queue('example_queue')

        make_request.assert_called_with('get', 'queues/example_queue')
        self.assertEqual(QUEUE_1, result)

    @mock.patch('SoftLayer.managers.messaging.MessagingConnection'
                '._make_request')
    def test_delete_queue(self, make_request):
        result = self.conn.delete_queue('example_queue')
        make_request.assert_called_with(
            'delete', 'queues/example_queue', params={})
        self.assertTrue(result)

        # With Force
        result = self.conn.delete_queue('example_queue', force=True)
        make_request.assert_called_with(
            'delete', 'queues/example_queue', params={'force': 1})
        self.assertTrue(result)

    @mock.patch('SoftLayer.managers.messaging.MessagingConnection'
                '._make_request')
    def test_push_queue_message(self, make_request):
        make_request().json.return_value = MESSAGE_1
        result = self.conn.push_queue_message('example_queue', '<body>')

        make_request.assert_called_with(
            'post', 'queues/example_queue/messages', data='{"body": "<body>"}')
        self.assertEqual(MESSAGE_1, result)

    @mock.patch('SoftLayer.managers.messaging.MessagingConnection'
                '._make_request')
    def test_pop_messages(self, make_request):
        make_request().json.return_value = MESSAGE_POP
        result = self.conn.pop_messages('example_queue')

        make_request.assert_called_with(
            'get', 'queues/example_queue/messages', params={'batch': 1})
        self.assertEqual(MESSAGE_POP, result)

    @mock.patch('SoftLayer.managers.messaging.MessagingConnection'
                '._make_request')
    def test_pop_message(self, make_request):
        make_request().json.return_value = MESSAGE_POP
        result = self.conn.pop_message('example_queue')

        make_request.assert_called_with(
            'get', 'queues/example_queue/messages', params={'batch': 1})
        self.assertEqual(MESSAGE_1, result)

    @mock.patch('SoftLayer.managers.messaging.MessagingConnection'
                '._make_request')
    def test_pop_message_empty(self, make_request):
        make_request().json.return_value = MESSAGE_POP_EMPTY
        result = self.conn.pop_message('example_queue')

        make_request.assert_called_with(
            'get', 'queues/example_queue/messages', params={'batch': 1})
        self.assertEqual(None, result)

    @mock.patch('SoftLayer.managers.messaging.MessagingConnection'
                '._make_request')
    def test_delete_message(self, make_request):
        result = self.conn.delete_message('example_queue', MESSAGE_1['id'])

        make_request.assert_called_with(
            'delete', 'queues/example_queue/messages/%s' % MESSAGE_1['id'])
        self.assertTrue(result)

    # Topic-based Tests
    @mock.patch('SoftLayer.managers.messaging.MessagingConnection'
                '._make_request')
    def test_get_topics(self, make_request):
        make_request().json.return_value = TOPIC_LIST
        result = self.conn.get_topics()

        make_request.assert_called_with('get', 'topics', params={})
        self.assertEqual(TOPIC_LIST, result)

        # with tags
        result = self.conn.get_topics(tags=['tag1', 'tag2'])

        make_request.assert_called_with(
            'get', 'topics', params={'tags': 'tag1,tag2'})
        self.assertEqual(TOPIC_LIST, result)

    @mock.patch('SoftLayer.managers.messaging.MessagingConnection'
                '._make_request')
    def test_create_topic(self, make_request):
        make_request().json.return_value = TOPIC_1
        result = self.conn.create_topic('example_topic')

        make_request.assert_called_with(
            'put', 'topics/example_topic', data='{}')
        self.assertEqual(TOPIC_1, result)

    @mock.patch('SoftLayer.managers.messaging.MessagingConnection'
                '._make_request')
    def test_modify_topic(self, make_request):
        make_request().json.return_value = TOPIC_1
        result = self.conn.modify_topic('example_topic')

        make_request.assert_called_with(
            'put', 'topics/example_topic', data='{}')
        self.assertEqual(TOPIC_1, result)

    @mock.patch('SoftLayer.managers.messaging.MessagingConnection'
                '._make_request')
    def test_get_topic(self, make_request):
        make_request().json.return_value = TOPIC_1
        result = self.conn.get_topic('example_topic')

        make_request.assert_called_with('get', 'topics/example_topic')
        self.assertEqual(TOPIC_1, result)

    @mock.patch('SoftLayer.managers.messaging.MessagingConnection'
                '._make_request')
    def test_delete_topic(self, make_request):
        result = self.conn.delete_topic('example_topic')
        make_request.assert_called_with(
            'delete', 'topics/example_topic', params={})
        self.assertTrue(result)

        # With Force
        result = self.conn.delete_topic('example_topic', force=True)
        make_request.assert_called_with(
            'delete', 'topics/example_topic', params={'force': 1})
        self.assertTrue(result)

    @mock.patch('SoftLayer.managers.messaging.MessagingConnection'
                '._make_request')
    def test_push_topic_message(self, make_request):
        make_request().json.return_value = MESSAGE_1
        result = self.conn.push_topic_message('example_topic', '<body>')

        make_request.assert_called_with(
            'post', 'topics/example_topic/messages', data='{"body": "<body>"}')
        self.assertEqual(MESSAGE_1, result)

    @mock.patch('SoftLayer.managers.messaging.MessagingConnection'
                '._make_request')
    def test_get_subscriptions(self, make_request):
        make_request().json.return_value = SUBSCRIPTION_LIST
        result = self.conn.get_subscriptions('example_topic')

        make_request.assert_called_with(
            'get', 'topics/example_topic/subscriptions')
        self.assertEqual(SUBSCRIPTION_LIST, result)

    @mock.patch('SoftLayer.managers.messaging.MessagingConnection'
                '._make_request')
    def test_create_subscription(self, make_request):
        make_request().json.return_value = SUBSCRIPTION_1
        endpoint_details = {
            'account_id': 'test',
            'queue_name': 'topic_subscription_queue'}
        result = self.conn.create_subscription(
            'example_topic', 'queue', **endpoint_details)

        make_request.assert_called_with(
            'post', 'topics/example_topic/subscriptions', data=mock.ANY)
        self.assertEqual(SUBSCRIPTION_1, result)

    @mock.patch('SoftLayer.managers.messaging.MessagingConnection.'
                '_make_request')
    def test_delete_subscription(self, make_request):
        make_request().json.return_value = SUBSCRIPTION_1
        result = self.conn.delete_subscription(
            'example_topic', SUBSCRIPTION_1['id'])

        make_request.assert_called_with(
            'delete',
            'topics/example_topic/subscriptions/%s' % SUBSCRIPTION_1['id'])
        self.assertTrue(result)
