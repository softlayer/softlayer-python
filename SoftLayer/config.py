"""
    SoftLayer.config
    ~~~~~~~~~~~~~~~~
    Handles different methods for loading configuration for the API bindings

    :license: MIT, see LICENSE for more details.
"""
import os
import os.path

from SoftLayer import auth
from SoftLayer import consts
from SoftLayer import transports
from SoftLayer import utils


def get_client_settings_args(**kwargs):
    """Retrieve client settings from user-supplied arguments.

        :param \\*\\*kwargs: Arguments that are passed into the client instance
    """
    return {
        'endpoint_url': kwargs.get('endpoint_url'),
        'timeout': kwargs.get('timeout'),
        'auth': kwargs.get('auth'),
        'transport': kwargs.get('transport'),
        'proxy': kwargs.get('proxy'),
        'username': kwargs.get('username'),
        'api_key': kwargs.get('api_key'),
    }


def get_client_settings_env(**_):
    """Retrieve client settings from environment settings.

        :param \\*\\*kwargs: Arguments that are passed into the client instance
    """

    return {
        'proxy': os.environ.get('https_proxy'),
        'username': os.environ.get('SL_USERNAME'),
        'api_key': os.environ.get('SL_API_KEY'),
    }


def get_client_settings_config_file(**kwargs):
    """Retrieve client settings from the possible config file locations.

        :param \\*\\*kwargs: Arguments that are passed into the client instance
    """
    config_files = ['/etc/softlayer.conf', '~/.softlayer']
    if kwargs.get('config_file'):
        config_files.append(kwargs.get('config_file'))
    config_files = [os.path.expanduser(f) for f in config_files]
    config = utils.configparser.RawConfigParser({
        'username': '',
        'api_key': '',
        'endpoint_url': '',
        'timeout': '',
        'proxy': '',
    })
    config.read(config_files)

    if not config.has_section('softlayer'):
        return

    return {
        'endpoint_url': config.get('softlayer', 'endpoint_url'),
        'timeout': config.get('softlayer', 'timeout'),
        'proxy': config.get('softlayer', 'proxy'),
        'username': config.get('softlayer', 'username'),
        'api_key': config.get('softlayer', 'api_key'),
    }


def set_transport_settings(settings):
    # Default the transport to use XMLRPC
    if 'transport' not in settings:
        settings['transport'] = transports.XmlRpcTransport()

    # If we have enough information to make auth, let's do it
    if all([settings.get('username'),
            settings.get('api_key'),
            settings.get('auth') is None,
            ]):

        # NOTE(kmcdonald): some transports mask other transports, so this is
        # a way to find the 'real' one
        real_transport = getattr(settings['transport'], 'transport',
                                 settings['transport'])

        # XMLRPC uses BasicAuthentication
        if isinstance(real_transport, transports.XmlRpcTransport):
            _auth = auth.BasicAuthentication(
                settings.get('username'),
                settings.get('api_key'),
            )
            settings['auth'] = _auth
            if 'endpoint_url' not in settings:
                settings['endpoint_url'] = consts.API_PUBLIC_ENDPOINT

        # REST uses BasicHTTPAuthentication
        elif isinstance(real_transport, transports.RestTransport):
            _auth = auth.BasicHTTPAuthentication(
                settings.get('username'),
                settings.get('api_key'),
            )
            settings['auth'] = _auth

            if 'endpoint_url' not in settings:
                settings['endpoint_url'] = consts.API_PUBLIC_ENDPOINT_REST


SETTING_RESOLVERS = [get_client_settings_args,
                     get_client_settings_env,
                     get_client_settings_config_file]


def get_client_settings(**kwargs):
    """Parse client settings.

    Parses settings from various input methods, preferring earlier values
    to later ones. Once an 'auth' value is found, it returns the gathered
    settings. The settings currently come from explicit user arguments,
    environmental variables and config files.

        :param \\*\\*kwargs: Arguments that are passed into the client instance
    """
    all_settings = {}
    for setting_method in SETTING_RESOLVERS:
        settings = setting_method(**kwargs)
        if settings:
            settings.update((k, v) for k, v in all_settings.items() if v)
            all_settings = settings

    set_transport_settings(all_settings)
    return all_settings
