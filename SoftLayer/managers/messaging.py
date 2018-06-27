"""
    SoftLayer.messaging
    ~~~~~~~~~~~~~~~~~~~
    Manager for the SoftLayer Message Queue service

    :license: MIT, see LICENSE for more details.
"""
import json

import requests.auth

from SoftLayer import consts
from SoftLayer import exceptions
# pylint: disable=no-self-use


ENDPOINTS = {
    "dal05": {
        "public": "dal05.mq.softlayer.net",
        "private": "dal05.mq.service.networklayer.com"
    }
}


class QueueAuth(requests.auth.AuthBase):
    """SoftLayer Message Queue authentication for requests.

    :param endpoint: endpoint URL
    :param username: SoftLayer username
    :param api_key: SoftLayer API Key
    :param auth_token: (optional) Starting auth token
    """

    def __init__(self, endpoint, username, api_key, auth_token=None):
        self.endpoint = endpoint
        self.username = username
        self.api_key = api_key
        self.auth_token = auth_token

    def auth(self):
        """Authenticate."""
        headers = {
            'X-Auth-User': self.username,
            'X-Auth-Key': self.api_key
        }
        resp = requests.post(self.endpoint, headers=headers)
        if resp.ok:
            self.auth_token = resp.headers['X-Auth-Token']
        else:
            raise exceptions.Unauthenticated("Error while authenticating: %s"
                                             % resp.status_code)

    def handle_error(self, resp, **_):
        """Handle errors."""
        resp.request.deregister_hook('response', self.handle_error)
        if resp.status_code == 503:
            resp.connection.send(resp.request)
        elif resp.status_code == 401:
            self.auth()
            resp.request.headers['X-Auth-Token'] = self.auth_token
            resp.connection.send(resp.request)

    def __call__(self, resp):
        """Attach auth token to the request.

        Do authentication if an auth token isn't available
        """
        if not self.auth_token:
            self.auth()
        resp.register_hook('response', self.handle_error)
        resp.headers['X-Auth-Token'] = self.auth_token
        return resp


class MessagingManager(object):
    """Manage SoftLayer Message Queue accounts.

    See product information here: http://www.softlayer.com/message-queue

    :param SoftLayer.API.BaseClient client: the client instance

    """

    def __init__(self, client):
        self.client = client

    def list_accounts(self, **kwargs):
        """List message queue accounts.

        :param dict \\*\\*kwargs: response-level options (mask, limit, etc.)
        """
        if 'mask' not in kwargs:
            items = [
                'id',
                'name',
                'status',
                'nodes',
            ]
            kwargs['mask'] = "mask[%s]" % ','.join(items)

        return self.client['Account'].getMessageQueueAccounts(**kwargs)

    def get_endpoint(self, datacenter=None, network=None):
        """Get a message queue endpoint based on datacenter/network type.

        :param datacenter: datacenter code
        :param network: network ('public' or 'private')
        """
        if datacenter is None:
            datacenter = 'dal05'
        if network is None:
            network = 'public'
        try:
            host = ENDPOINTS[datacenter][network]
            return "https://%s" % host
        except KeyError:
            raise TypeError('Invalid endpoint %s/%s'
                            % (datacenter, network))

    def get_endpoints(self):
        """Get all known message queue endpoints."""
        return ENDPOINTS

    def get_connection(self, account_id, datacenter=None, network=None):
        """Get connection to Message Queue Service.

        :param account_id: Message Queue Account id
        :param datacenter: Datacenter code
        :param network: network ('public' or 'private')
        """
        if any([not self.client.auth,
                not getattr(self.client.auth, 'username', None),
                not getattr(self.client.auth, 'api_key', None)]):
            raise exceptions.SoftLayerError(
                'Client instance auth must be BasicAuthentication.')

        client = MessagingConnection(
            account_id, endpoint=self.get_endpoint(datacenter, network))
        client.authenticate(self.client.auth.username,
                            self.client.auth.api_key)
        return client

    def ping(self, datacenter=None, network=None):
        """Ping a message queue endpoint."""
        resp = requests.get('%s/v1/ping' %
                            self.get_endpoint(datacenter, network))
        resp.raise_for_status()
        return True


class MessagingConnection(object):
    """Message Queue Service Connection.

    :param account_id: Message Queue Account id
    :param endpoint: Endpoint URL
    """

    def __init__(self, account_id, endpoint=None):
        self.account_id = account_id
        self.endpoint = endpoint
        self.auth = None

    def _make_request(self, method, path, **kwargs):
        """Make request. Generally not called directly.

        :param method: HTTP Method
        :param path: resource Path
        :param dict \\*\\*kwargs: extra request arguments
        """
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': consts.USER_AGENT,
        }
        headers.update(kwargs.get('headers', {}))
        kwargs['headers'] = headers
        kwargs['auth'] = self.auth

        url = '/'.join((self.endpoint, 'v1', self.account_id, path))
        resp = requests.request(method, url, **kwargs)
        try:
            resp.raise_for_status()
        except requests.HTTPError as ex:
            content = json.loads(ex.response.content)
            raise exceptions.SoftLayerAPIError(ex.response.status_code,
                                               content['message'])
        return resp

    def authenticate(self, username, api_key, auth_token=None):
        """Authenticate this connection using the given credentials.

        :param username: SoftLayer username
        :param api_key: SoftLayer API Key
        :param auth_token: (optional) Starting auth token
        """
        auth_endpoint = '/'.join((self.endpoint, 'v1',
                                  self.account_id, 'auth'))
        auth = QueueAuth(auth_endpoint, username, api_key,
                         auth_token=auth_token)
        auth.auth()
        self.auth = auth

    def stats(self, period='hour'):
        """Get account stats.

        :param period: 'hour', 'day', 'week', 'month'
        """
        resp = self._make_request('get', 'stats/%s' % period)
        return resp.json()

    # QUEUE METHODS

    def get_queues(self, tags=None):
        """Get listing of queues.

        :param list tags: (optional) list of tags to filter by
        """
        params = {}
        if tags:
            params['tags'] = ','.join(tags)
        resp = self._make_request('get', 'queues', params=params)
        return resp.json()

    def create_queue(self, queue_name, **kwargs):
        """Create Queue.

        :param queue_name: Queue Name
        :param dict \\*\\*kwargs: queue options
        """
        queue = {}
        queue.update(kwargs)
        data = json.dumps(queue)
        resp = self._make_request('put', 'queues/%s' % queue_name, data=data)
        return resp.json()

    def modify_queue(self, queue_name, **kwargs):
        """Modify Queue.

        :param queue_name: Queue Name
        :param dict \\*\\*kwargs: queue options
        """
        return self.create_queue(queue_name, **kwargs)

    def get_queue(self, queue_name):
        """Get queue details.

        :param queue_name: Queue Name
        """
        resp = self._make_request('get', 'queues/%s' % queue_name)
        return resp.json()

    def delete_queue(self, queue_name, force=False):
        """Delete Queue.

        :param queue_name: Queue Name
        :param force: (optional) Force queue to be deleted even if there
                      are pending messages
        """
        params = {}
        if force:
            params['force'] = 1
        self._make_request('delete', 'queues/%s' % queue_name, params=params)
        return True

    def push_queue_message(self, queue_name, body, **kwargs):
        """Create Queue Message.

        :param queue_name: Queue Name
        :param body: Message body
        :param dict \\*\\*kwargs: Message options
        """
        message = {'body': body}
        message.update(kwargs)
        resp = self._make_request('post', 'queues/%s/messages' % queue_name,
                                  data=json.dumps(message))
        return resp.json()

    def pop_messages(self, queue_name, count=1):
        """Pop messages from a queue.

        :param queue_name: Queue Name
        :param count: (optional) number of messages to retrieve
        """
        resp = self._make_request('get', 'queues/%s/messages' % queue_name,
                                  params={'batch': count})
        return resp.json()

    def pop_message(self, queue_name):
        """Pop a single message from a queue.

        If no messages are returned this returns None

        :param queue_name: Queue Name
        """
        messages = self.pop_messages(queue_name, count=1)
        if messages['item_count'] > 0:
            return messages['items'][0]
        else:
            return None

    def delete_message(self, queue_name, message_id):
        """Delete a message.

        :param queue_name: Queue Name
        :param message_id: Message id
        """
        self._make_request('delete', 'queues/%s/messages/%s'
                           % (queue_name, message_id))
        return True

    # TOPIC METHODS

    def get_topics(self, tags=None):
        """Get listing of topics.

        :param list tags: (optional) list of tags to filter by
        """
        params = {}
        if tags:
            params['tags'] = ','.join(tags)
        resp = self._make_request('get', 'topics', params=params)
        return resp.json()

    def create_topic(self, topic_name, **kwargs):
        """Create Topic.

        :param topic_name: Topic Name
        :param dict \\*\\*kwargs: Topic options
        """
        data = json.dumps(kwargs)
        resp = self._make_request('put', 'topics/%s' % topic_name, data=data)
        return resp.json()

    def modify_topic(self, topic_name, **kwargs):
        """Modify Topic.

        :param topic_name: Topic Name
        :param dict \\*\\*kwargs: Topic options
        """
        return self.create_topic(topic_name, **kwargs)

    def get_topic(self, topic_name):
        """Get topic details.

        :param topic_name: Topic Name
        """
        resp = self._make_request('get', 'topics/%s' % topic_name)
        return resp.json()

    def delete_topic(self, topic_name, force=False):
        """Delete Topic.

        :param topic_name: Topic Name
        :param force: (optional) Force topic to be deleted even if there
                      are attached subscribers
        """
        params = {}
        if force:
            params['force'] = 1
        self._make_request('delete', 'topics/%s' % topic_name, params=params)
        return True

    def push_topic_message(self, topic_name, body, **kwargs):
        """Create Topic Message.

        :param topic_name: Topic Name
        :param body: Message body
        :param dict \\*\\*kwargs: Topic message options
        """
        message = {'body': body}
        message.update(kwargs)
        resp = self._make_request('post', 'topics/%s/messages' % topic_name,
                                  data=json.dumps(message))
        return resp.json()

    def get_subscriptions(self, topic_name):
        """Listing of subscriptions on a topic.

        :param topic_name: Topic Name
        """
        resp = self._make_request('get',
                                  'topics/%s/subscriptions' % topic_name)
        return resp.json()

    def create_subscription(self, topic_name, subscription_type, **kwargs):
        """Create Subscription.

        :param topic_name: Topic Name
        :param subscription_type: type ('queue' or 'http')
        :param dict \\*\\*kwargs: Subscription options
        """
        resp = self._make_request(
            'post', 'topics/%s/subscriptions' % topic_name,
            data=json.dumps({
                'endpoint_type': subscription_type, 'endpoint': kwargs}))
        return resp.json()

    def delete_subscription(self, topic_name, subscription_id):
        """Delete a subscription.

        :param topic_name: Topic Name
        :param subscription_id: Subscription id
        """
        self._make_request('delete', 'topics/%s/subscriptions/%s' %
                           (topic_name, subscription_id))
        return True
