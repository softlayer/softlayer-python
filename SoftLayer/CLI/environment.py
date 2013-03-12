import sys
from importlib import import_module
from ConfigParser import SafeConfigParser
import os
import os.path

from SoftLayer.CLI.modules import get_module_list
from SoftLayer import API_PUBLIC_ENDPOINT


class Environment(object):
    # {'module_name': {'action': 'actionClass'}}
    plugins = {}
    aliases = {
        'meta': 'metadata',
        'my': 'metadata',
    }
    config = {}
    stdout = sys.stdout
    stderr = sys.stderr

    def get_module_name(self, module_name):
        if module_name in self.aliases:
            return self.aliases[module_name]
        return module_name

    def load_module(self, mod):  # pragma: no cover
        return import_module('SoftLayer.CLI.modules.%s' % mod)

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
            self.config = config
            return

        for config_name in ['username', 'api_key', 'endpoint_url']:
            if cp.get('softlayer', config_name):
                config[config_name] = cp.get('softlayer', config_name)

        self.config = config


class CLIRunnableType(type):

    env = Environment()

    def __init__(cls, name, bases, attrs):
        super(CLIRunnableType, cls).__init__(name, bases, attrs)
        if cls.env and name != 'CLIRunnable':
            cls.env.add_plugin(cls)
