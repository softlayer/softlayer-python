"""
usage: sl messaging [<command>] [<args>...] [options]

Manage SoftLayer Message Queue

The available commands are:
  list-accounts  List all queue accounts
  queue          Queue-related commands
  topic          Topic-related commands
"""
# :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
# :license: BSD, see LICENSE for more details.
# from SoftLayer import NetworkManager
import sys

from SoftLayer.CLI import CLIRunnable, Table
from SoftLayer.CLI.helpers import CLIAbort, listing, ArgumentError

try:
    import softlayer_messaging
except ImportError:
    raise CLIAbort("""This functionality requires the softlayer_messaging package.
Run 'pip install softlayer_messaging' to install.""")


def get_mq_client(account_id, env):
    client = softlayer_messaging.get_client(account_id)
    client.authenticate(env.config.get('username'), env.config.get('api_key'))
    return client


class ListAccounts(CLIRunnable):
    """
usage: sl messaging list-accounts [options]

List SoftLayer Message Queue Accounts

"""
    action = 'list-accounts'

    @staticmethod
    def execute(client, args):
        accounts = client['Account'].getMessageQueueAccounts(
            mask='id,name,status,nodes')

        t = Table([
            'id', 'name', 'status'
        ])
        for account in accounts:
            t.add_row([
                account['nodes'][0]['accountName'],
                account['name'],
                account['status']['name'],
            ])

        return t


def queue_table(queue):
    t = Table(['property', 'value'])
    t.align['property'] = 'r'
    t.align['value'] = 'l'

    t.add_row(['name', queue['name']])
    t.add_row(['message_count', queue['message_count']])
    t.add_row(['visible_message_count', queue['visible_message_count']])
    t.add_row(['tags', listing(queue['tags'] or [])])
    t.add_row(['expiration', queue['expiration']])
    t.add_row(['visibility_interval', queue['visibility_interval']])
    return t


def message_table(message):
    t = Table(['property', 'value'])
    t.align['property'] = 'r'
    t.align['value'] = 'l'

    t.add_row(['id', message['id']])
    t.add_row(['initial_entry_time', message['initial_entry_time']])
    t.add_row(['visibility_delay', message['visibility_delay']])
    t.add_row(['visibility_interval', message['visibility_interval']])
    t.add_row(['fields', message['fields']])
    return [t, message['body']]


def topic_table(topic):
    t = Table(['property', 'value'])
    t.align['property'] = 'r'
    t.align['value'] = 'l'

    t.add_row(['name', topic['name']])
    t.add_row(['tags', listing(topic['tags'] or [])])
    return t


def subscription_table(sub):
    t = Table(['property', 'value'])
    t.align['property'] = 'r'
    t.align['value'] = 'l'

    t.add_row(['id', sub['id']])
    t.add_row(['endpoint_type', sub['endpoint_type']])
    for k, v in sub['endpoint'].items():
        t.add_row([k, v])
    return t


class Queue(CLIRunnable):
    """
usage: sl messaging queue list <account_id> [options]
       sl messaging queue detail <account_id> <queue_name> [options]
       sl messaging queue create <account_id> <queue_name> [options]
       sl messaging queue modify <account_id> <queue_name> [options]
       sl messaging queue delete <account_id> <queue_name> [<message_id>] [options]
       sl messaging queue push <account_id> <queue_name> (<message> | [-]) [options]
       sl messaging queue pop <account_id> <queue_name>  [options]

Manage queues

Queue Create/modify Options:
  --visibility_interval=SECONDS  Time in seconds that messages will re-appear
                                   after being popped
  --expiration=SECONDS           Time in seconds that messages will live
  --tags=TAGS                    Comma-separated list of tags

Queue Delete Options:
  --force  Flag to force the deletion of the queue even when there are messages

Pop Options:
  --count=NUM  Count of messages to pop
"""
    action = 'queue'

    @classmethod
    def execute(cls, client, args):
        mq_client = get_mq_client(args['<account_id>'], cls.env)

        # list
        if args['list']:
            queues = mq_client.queues()['items']

            t = Table([
                'name', 'message_count', 'visible_message_count'
            ])
            for queue in queues:
                t.add_row([
                    queue['name'],
                    queue['message_count'],
                    queue['visible_message_count'],
                ])
            return t
        # detail
        elif args['detail']:
            queue = mq_client.queue(args['<queue_name>']).detail()
            return queue_table(queue)
        # create
        elif args['create'] or args['modify']:
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
        # delete
        elif args['delete']:
            if args['<message_id>']:
                messages = mq_client.queue(args['<queue_name>']).message(
                    args['<message_id>']).delete()
            else:
                mq_client.queue(args['<queue_name>']).delete(
                    args.get('--force'))
        # push message
        elif args['push']:
            # the message body comes from the positional argument or stdin
            body = ''
            if args['<message>'] is not None:
                body = args['<message>']
            else:
                body = sys.stdin.read()
            return message_table(
                mq_client.queue(args['<queue_name>']).push(body))
        # pop message
        elif args['pop']:
            messages = mq_client.queue(args['<queue_name>']).pop(
                args.get('--count') or 1)
            formatted_messages = []
            for message in messages['items']:
                formatted_messages.append(message_table(message))
            return formatted_messages
        else:
            raise CLIAbort('Invalid command')


class Topic(CLIRunnable):
    """
usage: sl messaging topic list <account_id> [options]
       sl messaging topic detail <account_id> <topic_name> [options]
       sl messaging topic create <account_id> <topic_name> [options]
       sl messaging topic delete <account_id> <topic_name> [<subscription_id>] [options]
       sl messaging topic push <account_id> <topic_name> (<message> | [-]) [options]

Manage topics and subscriptions

Topic/Subscription Create Options:
  --subscription        Create a subscription
  --type=TYPE           Type of endpoint, [Options: http, queue]
  --queue-name=NAME     Queue name. Required if --type is queue
  --http-method=METHOD  HTTP Method to use if --type is http
  --http-url=URL        HTTP/HTTPS URL to use. Required if --type is http
  --http-body=BODY      HTTP Body template to use if --type is http

Topic Delete Options:
  --force  Flag to force the deletion of the topic even when there are subscriptions

"""
    action = 'topic'

    @classmethod
    def execute(cls, client, args):
        mq_client = get_mq_client(args['<account_id>'], cls.env)

        # list
        if args['list']:
            topics = mq_client.topics()['items']

            t = Table(['name'])
            for topic in topics:
                t.add_row([topic['name']])
            return t
        # detail
        elif args['detail']:
            topic = mq_client.topic(args['<topic_name>']).detail()
            subscriptions = mq_client.topic(args['<topic_name>']).subscriptions()
            tables = []
            for sub in subscriptions['items']:
                tables.append(subscription_table(sub))
            return [topic_table(topic), tables]
        # create
        elif args['create']:
            if args['--subscription']:
                topic = mq_client.topic(args['<topic_name>'])
                if args['--type'] == 'queue':
                    subscription = topic.create_subscription(
                        'queue',
                        queue_name=args['--queue-name'],
                    )
                elif args['--type'] == 'http':
                    subscription = topic.create_subscription(
                        'http',
                        method=args['--http-method'] or 'GET',
                        url=args['--http-url'],
                        body=args['--http-body']
                    )
                else:
                    raise ArgumentError(
                        '--type should be either queue or http.')
                return subscription_table(subscription)
            else:
                tags = None
                if args.get('--tags'):
                    tags = [tag.strip() for tag in args.get('--tags').split(',')]

                topic = mq_client.create_topic(
                    args['<topic_name>'],
                    visibility_interval=int(args.get('--visibility_interval') or 30),
                    expiration=int(args.get('--expiration') or 604800),
                    tags=tags,
                )
                return topic_table(topic)
        # delete
        elif args['delete']:
            if args['<subscription_id>']:
                messages = mq_client.topic(args['<topic_name>']).subscription(
                    args['<subscription_id>']).delete()
            else:
                mq_client.topic(args['<topic_name>']).delete(
                    args.get('--force'))
        # push message
        elif args['push']:
            # the message body comes from the positional argument or stdin
            body = ''
            if args['<message>'] is not None:
                body = args['<message>']
            else:
                body = sys.stdin.read()
            return message_table(
                mq_client.topic(args['<topic_name>']).push(body))
        # pop message
        elif args['pop']:
            messages = mq_client.topic(args['<topic_name>']).pop(
                args.get('--count') or 1)
            formatted_messages = []
            for message in messages['items']:
                formatted_messages.append(message_table(message))
            return formatted_messages
        else:
            raise CLIAbort('Invalid command')
