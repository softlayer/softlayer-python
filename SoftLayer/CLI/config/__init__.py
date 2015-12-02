"""CLI configuration."""
# :license: MIT, see LICENSE for more details.

from SoftLayer.CLI import formatting


def _resolve_transport(transport):
    """recursively look for transports which refer to other transports."""
    nested_transport = getattr(transport, 'transport', None)
    if nested_transport is not None:
        return nested_transport

    return _resolve_transport(nested_transport)


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

    transport = _resolve_transport(client.transport)
    try:
        settings['timeout'] = transport.timeout
        settings['endpoint_url'] = transport.endpoint_url
    except AttributeError:
        pass

    return settings


def config_table(settings):
    """Returns a config table."""
    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'
    table.add_row(['Username', settings['username'] or 'not set'])
    table.add_row(['API Key', settings['api_key'] or 'not set'])
    table.add_row(['Endpoint URL', settings['endpoint_url'] or 'not set'])
    table.add_row(['Timeout', settings['timeout'] or 'not set'])
    return table
