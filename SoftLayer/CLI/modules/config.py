"""
usage: sl config [<command>] [<args>...] [options]

View and edit configuration

The available commands are:
  setup  Setup configuration
  show   Show current configuration
"""
# :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
# :license: BSD, see LICENSE for more details.

import os.path

from SoftLayer import (
    Client, SoftLayerAPIError, API_PUBLIC_ENDPOINT, API_PRIVATE_ENDPOINT)
from SoftLayer.CLI import CLIRunnable, CLIAbort, Table, confirm, format_output
import ConfigParser


def config_table(env):
    t = Table(['Name', 'Value'])
    t.align['Name'] = 'r'
    t.align['Value'] = 'l'
    config = env.config
    t.add_row(['Username', config.get('username', 'none set')])
    t.add_row(['API Key', config.get('api_key', 'none set')])
    t.add_row(['Endpoint URL', config.get('endpoint_url', 'none set')])
    return t


def get_api_key(username, secret, endpoint_url=None):
    # Try to use a client with username/api key
    try:
        client = Client(
            username=username,
            api_key=secret,
            endpoint_url=endpoint_url,
            timeout=5)

        client['Account'].getCurrentUser()
        return secret
    except SoftLayerAPIError as e:
        if 'invalid api token' not in e.faultString.lower():
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

    @classmethod
    def execute(cls, client, args):
        # User Input
        while True:
            username = cls.env.input(
                'Username [%s]: ' % cls.env.config['username']) \
                or cls.env.config['username']
            if username:
                break

        while True:
            secret = cls.env.getpass(
                'API Key or Password [%s]: ' % cls.env.config['api_key']) \
                or cls.env.config['api_key']
            if secret:
                break

        while True:
            endpoint_type = cls.env.input('Endpoint (public|private|custom): ')
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
                endpoint_url = cls.env.input(
                    'Endpoint URL [%s]: ' % cls.env.config['endpoint_url']
                ) or cls.env.config['endpoint_url']
                break

        api_key = get_api_key(username, secret, endpoint_url=endpoint_url)

        cls.env.config['username'] = username
        cls.env.config['api_key'] = api_key
        cls.env.config['endpoint_url'] = endpoint_url

        path = '~/.softlayer'
        if args.get('--config'):
            path = args.get('--config')
        config_path = os.path.expanduser(path)

        cls.env.out(format_output(config_table(cls.env)))

        if not confirm('Are you sure you want to write settings to "%s"?'
                       % config_path, default=True):
            raise CLIAbort('Aborted.')

        config = ConfigParser.RawConfigParser()
        config.add_section('softlayer')

        config.set('softlayer', 'username', cls.env.config['username'])
        config.set('softlayer', 'api_key', cls.env.config['api_key'])
        config.set('softlayer', 'endpoint_url', cls.env.config['endpoint_url'])

        f = os.fdopen(
            os.open(config_path, os.O_WRONLY | os.O_CREAT, 0600), 'w')
        try:
            config.write(f)
        finally:
            f.close()

        return "Configuration Updated Successfully"


class Show(CLIRunnable):
    """
usage: sl config show [options]

Show current configuration
"""
    action = 'show'

    @classmethod
    def execute(cls, client, args):
        return config_table(cls.env)
