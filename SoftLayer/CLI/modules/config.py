#!/usr/bin/env python
""" View and edit configuration """
import os.path

from SoftLayer.CLI import CLIRunnable, CLIAbort, Table, confirm
import ConfigParser


class Setup(CLIRunnable):
    """ Setup configuration """
    action = 'setup'

    @classmethod
    def execute(cls, client, args):
        username = cls.env.input('Username: ')
        api_key = cls.env.input('API Key: ')
        endpoint_url = cls.env.input('Endpoint URL: ')

        path = '~/.softlayer'
        if args.config:
            path = args.config

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
    """ Show configuration values """
    action = 'show'

    @classmethod
    def execute(cls, client, args):
        t = Table(['Name', 'Value'])
        t.align['Name'] = 'r'
        t.align['Value'] = 'l'
        config = cls.env.config
        t.add_row(['Username', config['username']])
        t.add_row(['API Key', config['api_key']])
        t.add_row(['Endpoint URL', config['endpoint_url']])
        return t
