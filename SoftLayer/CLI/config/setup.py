"""Setup CLI configuration."""
# :license: MIT, see LICENSE for more details.
import configparser
import os.path

import click

import SoftLayer
from SoftLayer.CLI import config
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting


def get_api_key(client, username, secret):
    """Attempts API-Key and password auth to get an API key.

    This will also generate an API key if one doesn't exist
    """

    # Try to use a client with username/api key
    if len(secret) == 64 or username == 'apikey':
        try:
            client['Account'].getCurrentUser()
            return secret
        except SoftLayer.SoftLayerAPIError as ex:
            if 'invalid api token' not in ex.faultString.lower():
                raise
    else:
        # Try to use a client with username/password
        client.authenticate_with_password(username, secret)

        user_record = client['Account'].getCurrentUser(mask='id, apiAuthenticationKeys')
        api_keys = user_record['apiAuthenticationKeys']
        if len(api_keys) == 0:
            return client['User_Customer'].addApiAuthenticationKey(id=user_record['id'])
        return api_keys[0]['authenticationKey']


@click.command()
@environment.pass_env
def cli(env):
    """Setup the ~/.softlayer file with username and apikey.

    Set the username to 'apikey' for cloud.ibm.com accounts.
    """

    username, secret, endpoint_url, timeout = get_user_input(env)
    new_client = SoftLayer.Client(username=username, api_key=secret, endpoint_url=endpoint_url, timeout=timeout)
    api_key = get_api_key(new_client, username, secret)

    path = '~/.softlayer'
    if env.config_file:
        path = env.config_file
    config_path = os.path.expanduser(path)

    env.out(env.fmt(config.config_table({'username': username,
                                         'api_key': api_key,
                                         'endpoint_url': endpoint_url,
                                         'timeout': timeout})))

    if not formatting.confirm('Are you sure you want to write settings '
                              'to "%s"?' % config_path, default=True):
        raise exceptions.CLIAbort('Aborted.')

    # Persist the config file. Read the target config file in before
    # setting the values to avoid clobbering settings
    parsed_config = configparser.RawConfigParser()
    parsed_config.read(config_path)
    try:
        parsed_config.add_section('softlayer')
    except configparser.DuplicateSectionError:
        pass

    parsed_config.set('softlayer', 'username', username)
    parsed_config.set('softlayer', 'api_key', api_key)
    parsed_config.set('softlayer', 'endpoint_url', endpoint_url)
    parsed_config.set('softlayer', 'timeout', timeout)

    config_fd = os.fdopen(os.open(config_path,
                                  (os.O_WRONLY | os.O_CREAT | os.O_TRUNC),
                                  0o600),
                          'w')
    try:
        parsed_config.write(config_fd)
    finally:
        config_fd.close()

    env.fout("Configuration Updated Successfully")


def get_user_input(env):
    """Ask for username, secret (api_key or password) and endpoint_url."""

    defaults = config.get_settings_from_client(env.client)

    # Ask for username
    username = env.input('Username', default=defaults['username'])

    # Ask for 'secret' which can be api_key or their password
    secret = env.getpass('API Key or Password', default=defaults['api_key'])

    # Ask for which endpoint they want to use
    endpoint = defaults.get('endpoint_url', 'public')
    endpoint_type = env.input(
        'Endpoint (public|private|custom)', default=endpoint)
    endpoint_type = endpoint_type.lower()

    if endpoint_type == 'public':
        endpoint_url = SoftLayer.API_PUBLIC_ENDPOINT
    elif endpoint_type == 'private':
        endpoint_url = SoftLayer.API_PRIVATE_ENDPOINT
    else:
        if endpoint_type == 'custom':
            endpoint_url = env.input('Endpoint URL', default=endpoint)
        else:
            endpoint_url = endpoint_type

    # Ask for timeout
    timeout = env.input('Timeout', default=defaults['timeout'] or 0)

    return username, secret, endpoint_url, timeout
