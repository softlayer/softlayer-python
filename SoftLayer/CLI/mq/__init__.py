"""Message queue service."""
# :license: MIT, see LICENSE for more details.

from SoftLayer.CLI import formatting


def queue_table(queue):
    """Returns a table with details about a queue."""
    table = formatting.Table(['property', 'value'])
    table.align['property'] = 'r'
    table.align['value'] = 'l'

    table.add_row(['name', queue['name']])
    table.add_row(['message_count', queue['message_count']])
    table.add_row(['visible_message_count', queue['visible_message_count']])
    table.add_row(['tags', formatting.listing(queue['tags'] or [])])
    table.add_row(['expiration', queue['expiration']])
    table.add_row(['visibility_interval', queue['visibility_interval']])
    return table


def message_table(message):
    """Returns a table with details about a message."""
    table = formatting.Table(['property', 'value'])
    table.align['property'] = 'r'
    table.align['value'] = 'l'

    table.add_row(['id', message['id']])
    table.add_row(['initial_entry_time', message['initial_entry_time']])
    table.add_row(['visibility_delay', message['visibility_delay']])
    table.add_row(['visibility_interval', message['visibility_interval']])
    table.add_row(['fields', message['fields']])
    return [table, message['body']]


def topic_table(topic):
    """Returns a table with details about a topic."""
    table = formatting.Table(['property', 'value'])
    table.align['property'] = 'r'
    table.align['value'] = 'l'

    table.add_row(['name', topic['name']])
    table.add_row(['tags', formatting.listing(topic['tags'] or [])])
    return table


def subscription_table(sub):
    """Returns a table with details about a subscription."""
    table = formatting.Table(['property', 'value'])
    table.align['property'] = 'r'
    table.align['value'] = 'l'

    table.add_row(['id', sub['id']])
    table.add_row(['endpoint_type', sub['endpoint_type']])
    for key, val in sub['endpoint'].items():
        table.add_row([key, val])
    return table
