"""CLI configuration."""
# :license: MIT, see LICENSE for more details.

from softlayer.cli import formatting


def get_settings_from_client(client):
    """Pull out settings from a softlayer.Client instance.

    :param client: softlayer.Client instance
    """
    settings = {
        'username': '',
        'api_key': '',
        'timeout': client.timeout or None,
        'endpoint_url': client.endpoint_url,
    }
    try:
        settings['username'] = client.auth.username
        settings['api_key'] = client.auth.api_key
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
