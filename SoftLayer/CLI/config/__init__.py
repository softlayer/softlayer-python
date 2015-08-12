"""CLI configuration."""
# :license: MIT, see LICENSE for more details.

from SoftLayer.CLI import formatting


def get_settings_from_client(client):
    """Pull out settings from a SoftLayer.BaseClient instance.

    :param client: SoftLayer.BaseClient instance
    """
    settings = {
        'username': '',
        'api_key': '',
        'timeout': '',
        'endpoint_url': '',
    }
    try:
        settings['username'] = client.auth.username
        settings['api_key'] = client.auth.api_key
    except AttributeError:
        pass

    try:
        settings['timeout'] = client.transport.transport.timeout
        settings['endpoint_url'] = client.transport.transport.endpoint_url
    except AttributeError:
        pass

    return settings


def config_table(settings):
    """Returns a config table."""
    table = formatting.KeyValueTable(['Name', 'Value'])
    table.align['Name'] = 'r'
    table.align['Value'] = 'l'
    table.add_row(['Username', settings['username'] or 'not set'])
    table.add_row(['API Key', settings['api_key'] or 'not set'])
    table.add_row(['Endpoint URL', settings['endpoint_url'] or 'not set'])
    table.add_row(['Timeout', settings['timeout'] or 'not set'])
    return table
