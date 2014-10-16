"""Setup CLI configuration"""
# :license: MIT, see LICENSE for more details.
import os.path

import SoftLayer
from SoftLayer import auth
from SoftLayer.CLI import config
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer import utils

import click


def get_api_key(client, username, secret, endpoint_url=None):
    """ Attempts API-Key and password auth to get an API key

    This will also generate an API key if one doesn't exist
    """

    client.endpoint_url = endpoint_url
    client.auth = None
    # Try to use a client with username/api key
    if len(secret) == 64:
        try:
            client.auth = auth.BasicAuthentication(username, secret)
            client['Account'].getCurrentUser()
            return secret
        except SoftLayer.SoftLayerAPIError as ex:
            if 'invalid api token' not in ex.faultString.lower():
                raise
    else:
        # Try to use a client with username/password
        client.authenticate_with_password(username, secret)

        user_record = client['Account'].getCurrentUser(
            mask='id, apiAuthenticationKeys')
        api_keys = user_record['apiAuthenticationKeys']
        if len(api_keys) == 0:
            return client['User_Customer'].addApiAuthenticationKey(
                id=user_record['id'])
        return api_keys[0]['authenticationKey']


@click.command()
@environment.pass_env
def cli(env):
    """Edit configuration"""

    username, secret, endpoint_url, timeout = get_user_input(env)

    api_key = get_api_key(env.client, username, secret,
                          endpoint_url=endpoint_url)

    path = '~/.softlayer'
    if env.config_file:
        path = env.config_file
    config_path = os.path.expanduser(path)

    env.out(
        formatting.format_output(config.config_table({
            'username': username,
            'api_key': api_key,
            'endpoint_url': endpoint_url,
            'timeout': timeout})))

    if not formatting.confirm('Are you sure you want to write settings '
                              'to "%s"?' % config_path, default=True):
        raise exceptions.CLIAbort('Aborted.')

    # Persist the config file. Read the target config file in before
    # setting the values to avoid clobbering settings
    parsed_config = utils.configparser.RawConfigParser()
    parsed_config.read(config_path)
    try:
        parsed_config.add_section('softlayer')
    except utils.configparser.DuplicateSectionError:
        pass

    parsed_config.set('softlayer', 'username', username)
    parsed_config.set('softlayer', 'api_key', api_key)
    parsed_config.set('softlayer', 'endpoint_url', endpoint_url)

    config_fd = os.fdopen(os.open(config_path,
                                  (os.O_WRONLY | os.O_CREAT | os.O_TRUNC),
                                  0o600),
                          'w')
    try:
        parsed_config.write(config_fd)
    finally:
        config_fd.close()

    return "Configuration Updated Successfully"


def get_user_input(env):
    """ Ask for username, secret (api_key or password) and endpoint_url """

    defaults = config.get_settings_from_client(env.client.real_client)
    timeout = defaults['timeout']

    # Ask for username
    for _ in range(3):
        username = (env.input('Username [%s]: ' % defaults['username'])
                    or defaults['username'])
        if username:
            break
    else:
        raise exceptions.CLIAbort('Aborted after 3 attempts')

    # Ask for 'secret' which can be api_key or their password
    for _ in range(3):
        secret = (env.getpass('API Key or Password [%s]: '
                              % defaults['api_key'])
                  or defaults['api_key'])
        if secret:
            break
    else:
        raise exceptions.CLIAbort('Aborted after 3 attempts')

    # Ask for which endpoint they want to use
    for _ in range(3):
        endpoint_type = env.input(
            'Endpoint (public|private|custom): ')
        endpoint_type = endpoint_type.lower()
        if not endpoint_type:
            endpoint_url = SoftLayer.API_PUBLIC_ENDPOINT
            break
        if endpoint_type == 'public':
            endpoint_url = SoftLayer.API_PUBLIC_ENDPOINT
            break
        elif endpoint_type == 'private':
            endpoint_url = SoftLayer.API_PRIVATE_ENDPOINT
            break
        elif endpoint_type == 'custom':
            endpoint_url = env.input(
                'Endpoint URL [%s]: ' % defaults['endpoint_url']
            ) or defaults['endpoint_url']
            break
    else:
        raise exceptions.CLIAbort('Aborted after 3 attempts')

    return username, secret, endpoint_url, timeout
