"""
    SoftLayer.CLI.environment
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    Abstracts everything related to the user's environment when running the CLI

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
import sys
import getpass
from importlib import import_module
from ConfigParser import SafeConfigParser
import os
import os.path

from SoftLayer.CLI.modules import get_module_list
from SoftLayer import API_PUBLIC_ENDPOINT, SoftLayerError


class InvalidCommand(SoftLayerError):
    " Raised when trying to use a command that does not exist "
    def __init__(self, module_name, command_name, *args):
        self.module_name = module_name
        self.command_name = command_name
        error = 'Invalid command: "%s".' % self.command_name
        SoftLayerError.__init__(self, error, *args)


class InvalidModule(SoftLayerError):
    " Raised when trying to use a module that does not exist "
    def __init__(self, module_name, *args):
        self.module_name = module_name
        error = 'Invalid module: "%s".' % self.module_name
        SoftLayerError.__init__(self, error, *args)


class Environment(object):
    # {'module_name': {'action': 'actionClass'}}
    plugins = {}
    aliases = {
        'meta': 'metadata',
        'my': 'metadata',
        'vm': 'cci',
        'hardware': 'server',
        'bmetal': 'bmc',
    }
    config = {}
    stdout = sys.stdout
    stderr = sys.stderr

    def get_command(self, module_name, command_name):
        actions = self.plugins.get(module_name) or {}
        if command_name in actions:
            return actions[command_name]
        if None in actions:
            return actions[None]
        raise InvalidCommand(module_name, command_name)

    def get_module_name(self, module_name):
        if module_name in self.aliases:
            return self.aliases[module_name]
        return module_name

    def load_module(self, module_name):  # pragma: no cover
        try:
            return import_module('SoftLayer.CLI.modules.%s' % module_name)
        except ImportError:
            raise InvalidModule(module_name)

    def add_plugin(self, cls):
        command = cls.__module__.split('.')[-1]
        if command not in self.plugins:
            self.plugins[command] = {}
        self.plugins[command][cls.action] = cls

    def plugin_list(self):
        return get_module_list()

    def out(self, s, nl=True):
        self.stdout.write(s)
        if nl:
            self.stdout.write(os.linesep)

    def err(self, s, nl=True):
        self.stderr.write(s)
        if nl:
            self.stderr.write(os.linesep)

    def input(self, prompt):
        return raw_input(prompt)

    def getpass(self, prompt):
        return getpass.getpass(prompt)

    def load_config(self, files):
        config_files = [os.path.expanduser(f) for f in files]

        cp = SafeConfigParser({
            'username': os.environ.get('SL_USERNAME') or '',
            'api_key': os.environ.get('SL_API_KEY') or '',
            'endpoint_url': API_PUBLIC_ENDPOINT,
        })
        cp.read(config_files)
        config = {}

        if not cp.has_section('softlayer'):
            cp.add_section('softlayer')

        for config_name in ['username', 'api_key', 'endpoint_url']:
            config[config_name] = cp.get('softlayer', config_name)

        self.config = config

    def exit(self, code=0):
        sys.exit(code)


class CLIRunnableType(type):

    env = Environment()

    def __init__(cls, name, bases, attrs):
        super(CLIRunnableType, cls).__init__(name, bases, attrs)
        if cls.env and name != 'CLIRunnable':
            cls.env.add_plugin(cls)


class CLIRunnable(object):
    __metaclass__ = CLIRunnableType
    options = []
    action = None

    @staticmethod
    def add_additional_args(parser):
        pass

    @staticmethod
    def execute(client, args):
        pass
