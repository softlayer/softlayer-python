"""
usage: sl config <command> [<args>...] [options]

View and edit configuration

The available commands are:
  setup  Setup configuration
  show   Show current configuration
"""
import os.path

from SoftLayer.CLI import CLIRunnable, CLIAbort, Table, confirm
import ConfigParser


class Setup(CLIRunnable):
    """
usage: sl config setup [options]

Setup configuration
"""
    action = 'setup'

    @classmethod
    def execute(cls, client, args):
        username = cls.env.input('Username: ')
        api_key = cls.env.input('API Key: ')
        endpoint_url = cls.env.input('Endpoint URL: ')

        path = '~/.softlayer'
        if args.get('--config'):
            path = args.get('--config')

        config_path = os.path.expanduser(path)
        c = confirm(
            'Are you sure you want to write settings to "%s"?' % config_path)

        if not c:
            raise CLIAbort('Aborted.')

        config = ConfigParser.RawConfigParser()
        config.add_section('softlayer')
        if username:
            config.set('softlayer', 'username', username)

        if api_key:
            config.set('softlayer', 'api_key', api_key)

        if endpoint_url:
            config.set('softlayer', 'endpoint_url', endpoint_url)

        f = open(config_path, 'w')
        try:
            config.write(f)
        finally:
            f.close()


class Show(CLIRunnable):
    """
usage: sl config show [options]

Show current configuration
"""
    action = 'show'

    @classmethod
    def execute(cls, client, args):
        t = Table(['Name', 'Value'])
        t.align['Name'] = 'r'
        t.align['Value'] = 'l'
        config = cls.env.config
        t.add_row(['Username', config.get('username', 'none set')])
        t.add_row(['API Key', config.get('api_kye', 'none set')])
        t.add_row(['Endpoint URL', config.get('endpoint_url', 'none set')])
        return t
