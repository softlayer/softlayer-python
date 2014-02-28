"""
    SoftLayer.config
    ~~~~~~~~~~~~~~~~
    Handles different methods for loading configuration for the API bindings

    :license: MIT, see LICENSE for more details.
"""
import os
import os.path

from .auth import BasicAuthentication
from SoftLayer.utils import configparser


def get_client_settings_args(**kwargs):
    """ Retreive client settings from user-supplied arguments

        :param \\*\\*kwargs: Arguments that are passed into the client instance
    """
    settings = {
        'endpoint_url': kwargs.get('endpoint_url'),
        'timeout': kwargs.get('timeout'),
        'auth': kwargs.get('auth'),
        'proxy': kwargs.get('proxy'),
    }
    username = kwargs.get('username')
    api_key = kwargs.get('api_key')
    if username and api_key and not settings['auth']:
        settings['auth'] = BasicAuthentication(username, api_key)
    return settings


def get_client_settings_env(**_):
    """ Retreive client settings from environment settings

        :param \\*\\*kwargs: Arguments that are passed into the client instance
    """
    username = os.environ.get('SL_USERNAME')
    api_key = os.environ.get('SL_API_KEY')
    proxy = os.environ.get('https_proxy')

    config = {'proxy': proxy}
    if username and api_key:
        config['auth'] = BasicAuthentication(username, api_key)
    return config


def get_client_settings_config_file(**kwargs):
    """ Retreive client settings from the possible config file locations

        :param \\*\\*kwargs: Arguments that are passed into the client instance
    """
    config_files = ['/etc/softlayer.conf', '~/.softlayer']
    if kwargs.get('config_file'):
        config_files.append(kwargs.get('config_file'))
    config_files = [os.path.expanduser(f) for f in config_files]
    config = configparser.RawConfigParser({
        'username': '',
        'api_key': '',
        'endpoint_url': '',
        'timeout': '',
        'proxy': '',
    })
    config.read(config_files)

    if not config.has_section('softlayer'):
        return

    settings = {
        'endpoint_url': config.get('softlayer', 'endpoint_url'),
        'timeout': config.get('softlayer', 'timeout'),
        'proxy': config.get('softlayer', 'proxy'),
    }
    username = config.get('softlayer', 'username')
    api_key = config.get('softlayer', 'api_key')
    if username and api_key:
        settings['auth'] = BasicAuthentication(username, api_key)
    return settings

SETTING_RESOLVERS = [get_client_settings_args,
                     get_client_settings_env,
                     get_client_settings_config_file]


def get_client_settings(**kwargs):
    """ Parses settings from various input methods, preferring earlier values
        to later ones. Once an 'auth' value is found, it returns the gathererd
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
            if all_settings.get('auth'):
                break
    return all_settings
