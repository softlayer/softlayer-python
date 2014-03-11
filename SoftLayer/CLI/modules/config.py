"""
usage: sl config [<command>] [<args>...] [options]

View and edit configuration

The available commands are:
  setup  Setup configuration
  show   Show current configuration
"""
# :license: MIT, see LICENSE for more details.

import os.path

from SoftLayer import (
    Client, SoftLayerAPIError, API_PUBLIC_ENDPOINT, API_PRIVATE_ENDPOINT)
from SoftLayer.CLI import (
    CLIRunnable, CLIAbort, KeyValueTable, confirm, format_output)
from SoftLayer.utils import configparser


def get_settings_from_client(client):
    """ Pull out settings from a SoftLayer.Client instance.

    :param client: SoftLayer.Client instance
    """
    settings = {
        'username': '',
        'api_key': '',
        'timeout': client.timeout or '',
        'endpoint_url': client.endpoint_url,
    }
    try:
        settings['username'] = client.auth.username
        settings['api_key'] = client.auth.api_key
    except AttributeError:
        pass

    return settings


def config_table(settings):
    """ Returns a config table """
    table = KeyValueTable(['Name', 'Value'])
    table.align['Name'] = 'r'
    table.align['Value'] = 'l'
    table.add_row(['Username', settings['username'] or 'not set'])
    table.add_row(['API Key', settings['api_key'] or 'not set'])
    table.add_row(['Endpoint URL', settings['endpoint_url'] or 'not set'])
    table.add_row(['Timeout', settings['timeout'] or 'not set'])
    return table


def get_api_key(username, secret, endpoint_url=None):
    """ Tries API-Key and password auth to get (and potentially generate) an
        API key. """
    # Try to use a client with username/api key
    try:
        client = Client(
            username=username,
            api_key=secret,
            endpoint_url=endpoint_url,
            timeout=5)

        client['Account'].getCurrentUser()
        return secret
    except SoftLayerAPIError as ex:
        if 'invalid api token' not in ex.faultString.lower():
            raise

    # Try to use a client with username/password
    client = Client(endpoint_url=endpoint_url, timeout=5)
    client.authenticate_with_password(username, secret)

    user_record = client['Account'].getCurrentUser(
        mask='id, apiAuthenticationKeys')
    api_keys = user_record['apiAuthenticationKeys']
    if len(api_keys) == 0:
        return client['User_Customer'].addApiAuthenticationKey(
            id=user_record['id'])
    return api_keys[0]['authenticationKey']


class Setup(CLIRunnable):
    """
usage: sl config setup [options]

Setup configuration
"""
    action = 'setup'

    def execute(self, args):
        settings = get_settings_from_client(self.client)

        # User Input
        # Ask for username
        while True:
            username = self.env.input(
                'Username [%s]: ' % settings['username']) \
                or settings['username']
            if username:
                break

        # Ask for 'secret' which can be api_key or their password
        while True:
            secret = self.env.getpass(
                'API Key or Password [%s]: ' % settings['api_key']) \
                or settings['api_key']
            if secret:
                break

        # Ask for which endpoint they want to use
        while True:
            endpoint_type = self.env.input(
                'Endpoint (public|private|custom): ')
            endpoint_type = endpoint_type.lower()
            if not endpoint_type:
                endpoint_url = API_PUBLIC_ENDPOINT
                break
            if endpoint_type == 'public':
                endpoint_url = API_PUBLIC_ENDPOINT
                break
            elif endpoint_type == 'private':
                endpoint_url = API_PRIVATE_ENDPOINT
                break
            elif endpoint_type == 'custom':
                endpoint_url = self.env.input(
                    'Endpoint URL [%s]: ' % settings['endpoint_url']
                ) or settings['endpoint_url']
                break

        api_key = get_api_key(username, secret, endpoint_url=endpoint_url)

        settings['username'] = username
        settings['api_key'] = api_key
        settings['endpoint_url'] = endpoint_url

        path = '~/.softlayer'
        if args.get('--config'):
            path = args.get('--config')
        config_path = os.path.expanduser(path)

        self.env.out(format_output(config_table(settings)))

        if not confirm('Are you sure you want to write settings to "%s"?'
                       % config_path, default=True):
            raise CLIAbort('Aborted.')

        # Persist the config file. Read the target config file in before
        # setting the values to avoid clobbering settings
        config = configparser.RawConfigParser()
        config.read(config_path)
        try:
            config.add_section('softlayer')
        except configparser.DuplicateSectionError:
            pass

        config.set('softlayer', 'username', settings['username'])
        config.set('softlayer', 'api_key', settings['api_key'])
        config.set('softlayer', 'endpoint_url', settings['endpoint_url'])

        config_file = os.fdopen(os.open(config_path,
                                        (os.O_WRONLY | os.O_CREAT),
                                        0o600),
                                'w')
        try:
            config.write(config_file)
        finally:
            config_file.close()

        return "Configuration Updated Successfully"


class Show(CLIRunnable):
    """
usage: sl config show [options]

Show current configuration
"""
    action = 'show'

    def execute(self, args):
        settings = get_settings_from_client(self.client)
        return config_table(settings)
