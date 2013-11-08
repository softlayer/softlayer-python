"""
    SoftLayer.CLI.environment
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    Abstracts everything related to the user's environment when running the CLI

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: MIT, see LICENSE for more details.
"""
import getpass
from importlib import import_module
import inspect
import os
import os.path
import sys

from SoftLayer.CLI.modules import get_module_list
from SoftLayer import SoftLayerError


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
        'hw': 'server',
        'bmetal': 'bmc',
    }
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
            module = import_module('SoftLayer.CLI.modules.%s' % module_name)
            for _, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, CLIRunnable):
                    self.add_plugin(obj)
            return module
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

    def exit(self, code=0):
        sys.exit(code)


class CLIRunnable(object):
    options = []  # set by subclass
    action = None  # set by subclass

    def __init__(self, client=None, env=None):
        self.client = client
        self.env = env

    def execute(self, args):
        pass
