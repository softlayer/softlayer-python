import json
import requests.auth

from SoftLayer.consts import USER_AGENT
from SoftLayer.exceptions import Unauthenticated

ENDPOINTS = {
    "dal05": {
        "public": "dal05.mq.softlayer.net",
        "private": "dal05.mq.service.networklayer.com"
    }
}


class QueueAuth(requests.auth.AuthBase):
    """ Message Queue authentication for requests

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
        """ Do Authentication """
        headers = {
            'X-Auth-User': self.username,
            'X-Auth-Key': self.api_key
        }
        resp = requests.post(self.endpoint, headers=headers)
        if resp.ok:
            self.auth_token = resp.headers['X-Auth-Token']
        else:
            raise Unauthenticated("Error while authenticating", resp)

    def handle_error(self, r, **kwargs):
        """ Handle errors """
        r.request.deregister_hook('response', self.handle_error)
        if r.status_code == 503:
            r.request.send(anyway=True)
        elif r.status_code == 401:
            self.auth()
            r.request.headers['X-Auth-Token'] = self.auth_token
            r.request.send(anyway=True)

    def __call__(self, r):
        """ Attach auth token to the request. Do authentication if an auth
            token isn't available
        """
        if not self.auth_token:
            self.auth()
        r.register_hook('response', self.handle_error)
        r.headers['X-Auth-Token'] = self.auth_token
        return r


class MessagingManager(object):
    """ Manage SoftLayer Message Queue """
    def __init__(self, client):
        self.client = client

    def list_accounts(self, **kwargs):
        """ List message queue accounts

        :param dict \*\*kwargs: response-level arguments (limit, offset, etc.)
        """
        if 'mask' not in kwargs:
            items = set([
                'id',
                'name',
                'status',
                'nodes',
            ])
            kwargs['mask'] = "mask[%s]" % ','.join(items)

        return self.client['Account'].getMessageQueueAccounts(**kwargs)

    def get_endpoint(self, datacenter=None, network=None):
        """ Get a message queue endpoint based on datacenter/network type

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
        """ Get all known message queue endpoints """
        return ENDPOINTS

    def get_connection(self, id, username, api_key, datacenter=None,
                       network=None):
        """ Get connection to Message Queue Service

        :param id: Message Queue Account id
        :param username: SoftLayer username
        :param api_key: SoftLayer API key
        :param datacenter: Datacenter code
        :param network: network ('public' or 'private')
        """
        client = MessagingConnection(
            id, endpoint=self.get_endpoint(datacenter, network))
        client.authenticate(username, api_key)
        return client

    def ping(self, datacenter=None, network=None):
        r = requests.get('%s/v1/ping' %
                         self.get_endpoint(datacenter, network))
        r.raise_for_status()
        return True


class MessagingConnection(object):
    """ Message Queue Service Connection

    :param id: Message Queue Account id
    :param endpoint: Endpoint URL
    """
    def __init__(self, id, endpoint=None):
        self.account_id = id
        self.endpoint = endpoint
        self.auth = None

    def _make_request(self, method, path, **kwargs):
        """ Make request. Generally not called directly

        :param method: HTTP Method
        :param path: resource Path
        :param dict \*\*kwargs: extra request arguments
        """
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': USER_AGENT,
        }
        headers.update(kwargs.get('headers', {}))
        kwargs['headers'] = headers
        kwargs['auth'] = self.auth

        url = '/'.join((self.endpoint, 'v1', self.account_id, path))
        r = requests.request(method, url, **kwargs)
        r.raise_for_status()
        return r

    def authenticate(self, username, api_key, auth_token=None):
        """ Make request. Generally not called directly

        :param username: SoftLayer username
        :param api_key: SoftLayer API Key
        :param auth_token: (optional) Starting auth token
        """
        auth_endpoint = '/'.join((self.endpoint, 'v1', self.account_id, 'auth'))
        auth = QueueAuth(auth_endpoint, username, api_key,
                         auth_token=auth_token)
        auth.auth()
        self.auth = auth

    def stats(self, period='hour'):
        """ Get account stats

        :param period: 'hour', 'day', 'week', 'month'
        """
        r = self._make_request('get', 'stats/%s' % period)
        return json.loads(r.content)

    # QUEUE METHODS

    def get_queues(self, tags=None):
        """ Get listing of queues

        :param list tags: (optional) list of tags to filter by
        """
        params = {}
        if tags:
            params['tags'] = ','.join(tags)
        r = self._make_request('get', 'queues', params=params)
        return json.loads(r.content)

    def create_queue(self, queue_name, **kwargs):
        """ Create Queue

        :param queue_name: Queue Name
        :param dict \*\*kwargs: queue options
        """
        queue = {}
        queue.update(kwargs)
        data = json.dumps(queue)
        r = self._make_request('put', 'queues/%s' % queue_name, data=data)
        return json.loads(r.content)

    def modify_queue(self, queue_name, **kwargs):
        """ Modify Queue

        :param queue_name: Queue Name
        :param dict \*\*kwargs: queue options
        """
        return self.create_queue(queue_name, **kwargs)

    def get_queue(self, queue_name):
        """ Get queue details

        :param queue_name: Queue Name
        """
        r = self._make_request('get', 'queues/%s' % queue_name)
        return json.loads(r.content)

    def delete_queue(self, queue_name, force=False):
        """ Delete Queue

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
        """ Create Queue Message

        :param queue_name: Queue Name
        :param body: Message body
        :param dict \*\*kwargs: Message options
        """
        message = {'body': body}
        message.update(kwargs)
        r = self._make_request('post', 'queues/%s/messages' % queue_name,
                              data=json.dumps(message))
        return json.loads(r.content)

    def pop_message(self, queue_name, count=1):
        """ Pop message from a queue

        :param queue_name: Queue Name
        :param count: (optional) number of messages to retrieve
        """
        r = self._make_request('get', 'queues/%s/messages' % queue_name,
                              params={'batch': count})
        return json.loads(r.content)

    def delete_message(self, queue_name, message_id):
        """ Delete a message

        :param queue_name: Queue Name
        :param message_id: Message id
        """
        self._make_request('delete', 'queues/%s/messages/%s'
                          % (queue_name, message_id))
        return True

    # TOPIC METHODS

    def get_topics(self, tags=None):
        """ Get listing of topics

        :param list tags: (optional) list of tags to filter by
        """
        params = {}
        if tags:
            params['tags'] = ','.join(tags)
        r = self._make_request('get', 'topics', params=params)
        return json.loads(r.content)

    def create_topic(self, topic_name, **kwargs):
        """ Create Topic

        :param topic_name: Topic Name
        :param dict \*\*kwargs: Topic options
        """
        data = json.dumps(kwargs)
        r = self._make_request('put', 'topics/%s' % topic_name, data=data)
        return json.loads(r.content)

    def modify_topic(self, topic_name, **kwargs):
        """ Modify Topic

        :param topic_name: Topic Name
        :param dict \*\*kwargs: Topic options
        """
        return self.create_topic(topic_name, **kwargs)

    def get_topic(self, topic_name):
        """ Get topic details

        :param topic_name: Topic Name
        """
        r = self._make_request('get', 'topics/%s' % topic_name)
        return json.loads(r.content)

    def delete_topic(self, topic_name, force=False):
        """ Delete Topic

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
        """ Create Topic Message

        :param topic_name: Topic Name
        :param body: Message body
        :param dict \*\*kwargs: Topic message options
        """
        message = {'body': body}
        message.update(kwargs)
        r = self._make_request('post', 'topics/%s/messages' % topic_name,
                              data=json.dumps(message))
        return json.loads(r.content)

    def get_subscriptions(self, topic_name):
        """ Listing of subscriptions on a topic

        :param topic_name: Topic Name
        """
        r = self._make_request('get', 'topics/%s/subscriptions' % topic_name)
        return json.loads(r.content)

    def create_subscription(self, topic_name, type, **kwargs):
        """ Create Subscription

        :param topic_name: Topic Name
        :param type: type ('queue' or 'http')
        :param dict \*\*kwargs: Subscription options
        """
        r = self._make_request(
            'post', 'topics/%s/subscriptions' % topic_name,
            data=json.dumps({'endpoint_type': type, 'endpoint': kwargs}))
        return json.loads(r.content)

    def delete_subscription(self, topic_name, subscription_id):
        """ Delete a subscription

        :param topic_name: Topic Name
        :param subscription_id: Subscription id
        """
        self._make_request('delete', 'topics/%s/subscriptions/%s' %
                          (topic_name, subscription_id))
        return True

