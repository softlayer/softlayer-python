"""
usage: sl config [<command>] [<args>...] [options]

View and edit configuration

The available commands are:
  setup  Setup configuration
  show   Show current configuration
"""
# :license: MIT, see LICENSE for more details.

import os.path

import SoftLayer
from SoftLayer import auth
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer import utils


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
    table = formatting.KeyValueTable(['Name', 'Value'])
    table.align['Name'] = 'r'
    table.align['Value'] = 'l'
    table.add_row(['Username', settings['username'] or 'not set'])
    table.add_row(['API Key', settings['api_key'] or 'not set'])
    table.add_row(['Endpoint URL', settings['endpoint_url'] or 'not set'])
    table.add_row(['Timeout', settings['timeout'] or 'not set'])
    return table


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


class Setup(environment.CLIRunnable):
    """
usage: sl config setup [options]

Setup configuration
"""
    action = 'setup'

    def execute(self, args):
        username, secret, endpoint_url, timeout = self.get_user_input()

        api_key = get_api_key(self.client, username, secret,
                              endpoint_url=endpoint_url)

        path = '~/.softlayer'
        if args.get('--config'):
            path = args.get('--config')
        config_path = os.path.expanduser(path)

        self.env.out(
            formatting.format_output(config_table({
                'username': username,
                'api_key': api_key,
                'endpoint_url': endpoint_url,
                'timeout': timeout})))

        if not formatting.confirm('Are you sure you want to write settings '
                                  'to "%s"?' % config_path, default=True):
            raise exceptions.CLIAbort('Aborted.')

        # Persist the config file. Read the target config file in before
        # setting the values to avoid clobbering settings
        config = utils.configparser.RawConfigParser()
        config.read(config_path)
        try:
            config.add_section('softlayer')
        except utils.configparser.DuplicateSectionError:
            pass

        config.set('softlayer', 'username', username)
        config.set('softlayer', 'api_key', api_key)
        config.set('softlayer', 'endpoint_url', endpoint_url)

        config_file = os.fdopen(os.open(config_path,
                                        (os.O_WRONLY | os.O_CREAT),
                                        0o600),
                                'w')
        try:
            config.write(config_file)
        finally:
            config_file.close()

        return "Configuration Updated Successfully"

    def get_user_input(self):
        """ Ask for username, secret (api_key or password) and endpoint_url """

        defaults = get_settings_from_client(self.client)
        timeout = defaults['timeout']

        # Ask for username
        for _ in range(3):
            username = (self.env.input('Username [%s]: '
                                       % defaults['username'])
                        or defaults['username'])
            if username:
                break
        else:
            raise exceptions.CLIAbort('Aborted after 3 attempts')

        # Ask for 'secret' which can be api_key or their password
        for _ in range(3):
            secret = (self.env.getpass('API Key or Password [%s]: '
                                       % defaults['api_key'])
                      or defaults['api_key'])
            if secret:
                break
        else:
            raise exceptions.CLIAbort('Aborted after 3 attempts')

        # Ask for which endpoint they want to use
        for _ in range(3):
            endpoint_type = self.env.input(
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
                endpoint_url = self.env.input(
                    'Endpoint URL [%s]: ' % defaults['endpoint_url']
                ) or defaults['endpoint_url']
                break
        else:
            raise exceptions.CLIAbort('Aborted after 3 attempts')

        return username, secret, endpoint_url, timeout


class Show(environment.CLIRunnable):
    """
usage: sl config show [options]

Show current configuration
"""
    action = 'show'

    def execute(self, args):
        settings = get_settings_from_client(self.client)
        return config_table(settings)
