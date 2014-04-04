"""
usage: sl messaging [<command>] [<args>...] [options]

Manage the SoftLayer Message Queue service. For most commands, a queue account
is required. Use 'sl messaging accounts-list' to list current accounts

The available commands are:
  accounts-list      List all queue accounts
  endpoints-list     List all service endpoints
  ping               Ping the service

  queue-add          Create a new queue
  queue-detail       Prints the details of a queue
  queue-edit         Modifies an existing queue
  queue-list         Lists out all queues on an account
  queue-pop          Pop a message from a queue
  queue-push         Pushes a message into a queue
  queue-remove       Delete a queue

  topic-add          Creates a new topic
  topic-detail       Prints the details of a topic
  topic-list         Lists out all topics on an account
  topic-push         Pushes a notification to a topic
  topic-remove       Deletes a topic
  topic-subscribe    Adds a subscription on a topic
  topic-unsubscribe  Remove a subscription on a topic

"""
# :license: MIT, see LICENSE for more details.
# Missing docstrings ignored due to __doc__ = __doc__ magic
# pylint: disable=C0111
import sys

from SoftLayer import MessagingManager
from SoftLayer.CLI import CLIRunnable, Table
from SoftLayer.CLI.helpers import CLIAbort, listing, ArgumentError, blank


COMMON_MESSAGING_ARGS = """Service Options:
  --datacenter=NAME  Datacenter, E.G.: dal05
  --network=TYPE     Network type, [Options: public, private]
"""


class ListAccounts(CLIRunnable):
    """
usage: sl messaging accounts-list [options]

List SoftLayer Message Queue Accounts

"""
    action = 'accounts-list'

    def execute(self, args):
        manager = MessagingManager(self.client)
        accounts = manager.list_accounts()

        table = Table([
            'id', 'name', 'status'
        ])
        for account in accounts:
            if not account['nodes']:
                continue

            table.add_row([
                account['nodes'][0]['accountName'],
                account['name'],
                account['status']['name'],
            ])

        return table


class ListEndpoints(CLIRunnable):
    """
usage: sl messaging endpoints-list [options]

List SoftLayer Message Queue Endpoints

"""
    action = 'endpoints-list'

    def execute(self, args):
        manager = MessagingManager(self.client)
        regions = manager.get_endpoints()

        table = Table([
            'name', 'public', 'private'
        ])
        for region, endpoints in regions.items():
            table.add_row([
                region,
                endpoints.get('public') or blank(),
                endpoints.get('private') or blank(),
            ])

        return table


class Ping(CLIRunnable):
    __doc__ = """
usage: sl messaging ping [options]

Ping the SoftLayer Message Queue service

""" + COMMON_MESSAGING_ARGS
    action = 'ping'

    def execute(self, args):
        manager = MessagingManager(self.client)
        okay = manager.ping(
            datacenter=args['--datacenter'], network=args['--network'])
        if okay:
            return 'OK'
        else:
            CLIAbort('Ping failed')


def queue_table(queue):
    """ Returns a table with details about a queue """
    table = Table(['property', 'value'])
    table.align['property'] = 'r'
    table.align['value'] = 'l'

    table.add_row(['name', queue['name']])
    table.add_row(['message_count', queue['message_count']])
    table.add_row(['visible_message_count', queue['visible_message_count']])
    table.add_row(['tags', listing(queue['tags'] or [])])
    table.add_row(['expiration', queue['expiration']])
    table.add_row(['visibility_interval', queue['visibility_interval']])
    return table


def message_table(message):
    """ Returns a table with details about a message """
    table = Table(['property', 'value'])
    table.align['property'] = 'r'
    table.align['value'] = 'l'

    table.add_row(['id', message['id']])
    table.add_row(['initial_entry_time', message['initial_entry_time']])
    table.add_row(['visibility_delay', message['visibility_delay']])
    table.add_row(['visibility_interval', message['visibility_interval']])
    table.add_row(['fields', message['fields']])
    return [table, message['body']]


def topic_table(topic):
    """ Returns a table with details about a topic """
    table = Table(['property', 'value'])
    table.align['property'] = 'r'
    table.align['value'] = 'l'

    table.add_row(['name', topic['name']])
    table.add_row(['tags', listing(topic['tags'] or [])])
    return table


def subscription_table(sub):
    """ Returns a table with details about a subscription """
    table = Table(['property', 'value'])
    table.align['property'] = 'r'
    table.align['value'] = 'l'

    table.add_row(['id', sub['id']])
    table.add_row(['endpoint_type', sub['endpoint_type']])
    for key, val in sub['endpoint'].items():
        table.add_row([key, val])
    return table


class QueueList(CLIRunnable):
    __doc__ = """
usage: sl messaging queue-list <account_id> [options]

List all queues on an account

""" + COMMON_MESSAGING_ARGS
    action = 'queue-list'

    def execute(self, args):
        manager = MessagingManager(self.client)
        mq_client = manager.get_connection(args['<account_id>'])

        queues = mq_client.get_queues()['items']

        table = Table([
            'name', 'message_count', 'visible_message_count'
        ])
        for queue in queues:
            table.add_row([
                queue['name'],
                queue['message_count'],
                queue['visible_message_count'],
            ])
        return table


class QueueDetail(CLIRunnable):
    __doc__ = """
usage: sl messaging queue-detail <account_id> <queue_name> [options]

Detail a queue

""" + COMMON_MESSAGING_ARGS
    action = 'queue-detail'

    def execute(self, args):
        manager = MessagingManager(self.client)
        mq_client = manager.get_connection(args['<account_id>'])
        queue = mq_client.get_queue(args['<queue_name>'])
        return queue_table(queue)


class QueueCreate(CLIRunnable):
    __doc__ = """
usage: sl messaging queue-add <account_id> <queue_name> [options]

Create a queue

Options:
  --visibility_interval=SECONDS  Time in seconds that messages will re-appear
                                   after being popped
  --expiration=SECONDS           Time in seconds that messages will live
  --tags=TAGS                    Comma-separated list of tags

""" + COMMON_MESSAGING_ARGS
    action = 'queue-add'

    def execute(self, args):
        manager = MessagingManager(self.client)
        mq_client = manager.get_connection(args['<account_id>'])
        tags = None
        if args.get('--tags'):
            tags = [tag.strip() for tag in args.get('--tags').split(',')]

        queue = mq_client.create_queue(
            args['<queue_name>'],
            visibility_interval=int(args.get('--visibility_interval') or 30),
            expiration=int(args.get('--expiration') or 604800),
            tags=tags,
        )
        return queue_table(queue)


class QueueModify(CLIRunnable):
    __doc__ = """
usage: sl messaging queue-edit <account_id> <queue_name> [options]

Modify a queue

Options:
  --visibility_interval=SECONDS  Time in seconds that messages will re-appear
                                   after being popped
  --expiration=SECONDS           Time in seconds that messages will live
  --tags=TAGS                    Comma-separated list of tags

""" + COMMON_MESSAGING_ARGS
    action = 'queue-edit'

    def execute(self, args):
        manager = MessagingManager(self.client)
        mq_client = manager.get_connection(args['<account_id>'])
        tags = None
        if args.get('--tags'):
            tags = [tag.strip() for tag in args.get('--tags').split(',')]

        queue = mq_client.create_queue(
            args['<queue_name>'],
            visibility_interval=int(args.get('--visibility_interval') or 30),
            expiration=int(args.get('--expiration') or 604800),
            tags=tags,
        )
        return queue_table(queue)


class QueueDelete(CLIRunnable):
    __doc__ = """
usage: sl messaging queue-remove <account_id> <queue_name> [<message_id>]
                                 [options]

Delete a queue or a queued message

Options:
  --force  Flag to force the deletion of the queue even when there are messages

""" + COMMON_MESSAGING_ARGS
    action = 'queue-remove'

    def execute(self, args):
        manager = MessagingManager(self.client)
        mq_client = manager.get_connection(args['<account_id>'])

        if args['<message_id>']:
            mq_client.delete_message(args['<queue_name>'],
                                     args['<message_id>'])
        else:
            mq_client.delete_queue(args['<queue_name>'], args.get('--force'))


class QueuePush(CLIRunnable):
    __doc__ = """
usage: sl messaging queue-push <account_id> <queue_name> (<message> | -)
                               [options]

Push a message into a queue

Options:
  --force  Flag to force the deletion of the queue even when there are messages

""" + COMMON_MESSAGING_ARGS
    action = 'queue-push'

    def execute(self, args):
        manager = MessagingManager(self.client)
        mq_client = manager.get_connection(args['<account_id>'])
        body = ''
        if args['<message>'] == '-':
            body = sys.stdin.read()
        else:
            body = args['<message>']
        return message_table(
            mq_client.push_queue_message(args['<queue_name>'], body))


class QueuePop(CLIRunnable):
    __doc__ = """
usage: sl messaging queue-pop <account_id> <queue_name>  [options]

Pops a message from a queue

Options:
  --count=NUM     Count of messages to pop
  --delete-after  Remove popped messages from the queue

""" + COMMON_MESSAGING_ARGS
    action = 'queue-pop'

    def execute(self, args):
        manager = MessagingManager(self.client)
        mq_client = manager.get_connection(args['<account_id>'])

        messages = mq_client.pop_messages(
            args['<queue_name>'],
            args.get('--count') or 1)
        formatted_messages = []
        for message in messages['items']:
            formatted_messages.append(message_table(message))

        if args.get('--delete-after'):
            for message in messages['items']:
                mq_client.delete_message(
                    args['<queue_name>'],
                    message['id'])
        return formatted_messages


class TopicList(CLIRunnable):
    __doc__ = """
usage: sl messaging topic-list <account_id> [options]

List all topics on an account

""" + COMMON_MESSAGING_ARGS
    action = 'topic-list'

    def execute(self, args):
        manager = MessagingManager(self.client)
        mq_client = manager.get_connection(args['<account_id>'])
        topics = mq_client.get_topics()['items']

        table = Table(['name'])
        for topic in topics:
            table.add_row([topic['name']])
        return table


class TopicDetail(CLIRunnable):
    __doc__ = """
usage: sl messaging topic-detail <account_id> <topic_name> [options]

Detail a topic

""" + COMMON_MESSAGING_ARGS
    action = 'topic-detail'

    def execute(self, args):
        manager = MessagingManager(self.client)
        mq_client = manager.get_connection(args['<account_id>'])
        topic = mq_client.get_topic(args['<topic_name>'])
        subscriptions = mq_client.get_subscriptions(args['<topic_name>'])
        tables = []
        for sub in subscriptions['items']:
            tables.append(subscription_table(sub))
        return [topic_table(topic), tables]


class TopicCreate(CLIRunnable):
    __doc__ = """
usage: sl messaging topic-add <account_id> <topic_name> [options]

Create a new topic

""" + COMMON_MESSAGING_ARGS
    action = 'topic-add'

    def execute(self, args):
        manager = MessagingManager(self.client)
        mq_client = manager.get_connection(args['<account_id>'])
        tags = None
        if args.get('--tags'):
            tags = [tag.strip() for tag in args.get('--tags').split(',')]

        topic = mq_client.create_topic(
            args['<topic_name>'],
            visibility_interval=int(
                args.get('--visibility_interval') or 30),
            expiration=int(args.get('--expiration') or 604800),
            tags=tags,
        )
        return topic_table(topic)


class TopicDelete(CLIRunnable):
    __doc__ = """
usage: sl messaging topic-remove <account_id> <topic_name> [options]

Delete a topic or subscription

Options:
  --force  Flag to force the deletion of the topic even when there are
             subscriptions
""" + COMMON_MESSAGING_ARGS
    action = 'topic-remove'

    def execute(self, args):
        manager = MessagingManager(self.client)
        mq_client = manager.get_connection(args['<account_id>'])
        mq_client.delete_topic(args['<topic_name>'], args.get('--force'))


class TopicSubscribe(CLIRunnable):
    __doc__ = """
usage: sl messaging topic-subscribe <account_id> <topic_name> [options]

Create a subscription on a topic

Options:
  --type=TYPE           Type of endpoint, [Options: http, queue]
  --queue-name=NAME     Queue name. Required if --type is queue
  --http-method=METHOD  HTTP Method to use if --type is http
  --http-url=URL        HTTP/HTTPS URL to use. Required if --type is http
  --http-body=BODY      HTTP Body template to use if --type is http

""" + COMMON_MESSAGING_ARGS
    action = 'topic-subscribe'

    def execute(self, args):
        manager = MessagingManager(self.client)
        mq_client = manager.get_connection(args['<account_id>'])
        if args['--type'] == 'queue':
            subscription = mq_client.create_subscription(
                args['<topic_name>'],
                'queue',
                queue_name=args['--queue-name'],
            )
        elif args['--type'] == 'http':
            subscription = mq_client.create_subscription(
                args['<topic_name>'],
                'http',
                method=args['--http-method'] or 'GET',
                url=args['--http-url'],
                body=args['--http-body']
            )
        else:
            raise ArgumentError(
                '--type should be either queue or http.')
        return subscription_table(subscription)


class TopicUnsubscribe(CLIRunnable):
    __doc__ = """
usage: sl messaging topic-unsubscribe <account_id> <topic_name>
                                      <subscription_id> [options]

Remove a subscription on a topic

""" + COMMON_MESSAGING_ARGS
    action = 'topic-unsubscribe'

    def execute(self, args):
        manager = MessagingManager(self.client)
        mq_client = manager.get_connection(args['<account_id>'])

        mq_client.delete_subscription(
            args['<topic_name>'],
            args['<subscription_id>'])


class TopicPush(CLIRunnable):
    __doc__ = """
usage: sl messaging topic-push <account_id> <topic_name> (<message> | -)
                               [options]

Push a message into a topic

""" + COMMON_MESSAGING_ARGS
    action = 'topic-push'

    def execute(self, args):
        manager = MessagingManager(self.client)
        mq_client = manager.get_connection(args['<account_id>'])

        # the message body comes from the positional argument or stdin
        body = ''
        if args['<message>'] == '-':
            body = sys.stdin.read()
        else:
            body = args['<message>']
        return message_table(
            mq_client.push_topic_message(args['<topic_name>'], body))
