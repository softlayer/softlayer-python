"""
    SoftLayer.CLI.environment
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    Abstracts everything related to the user's environment when running the CLI

    :license: MIT, see LICENSE for more details.
"""
import getpass
from importlib import import_module
import inspect
import os
import os.path
import sys

from SoftLayer.CLI.modules import get_module_list
from SoftLayer.utils import console_input
from SoftLayer import SoftLayerError

# pylint: disable=R0201


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
    """ Provides access to the current CLI environment """
    def __init__(self):
        # {'module_name': {'action': 'actionClass'}}
        self.plugins = {}
        self.aliases = {
            'meta': 'metadata',
            'my': 'metadata',
            'vm': 'vs',
            'cci': 'vs',
            'hardware': 'server',
            'hw': 'server',
            'bmetal': 'bmc',
            'virtual': 'vs',
            'lb': 'loadbal',
        }
        self.stdout = sys.stdout
        self.stderr = sys.stderr

    def get_command(self, module_name, command_name):
        """ Based on the loaded modules, return a command """
        actions = self.plugins.get(module_name) or {}
        if command_name in actions:
            return actions[command_name]
        if None in actions:
            return actions[None]
        raise InvalidCommand(module_name, command_name)

    def get_module_name(self, module_name):
        """ Returns the actual module name. Uses the alias mapping """
        if module_name in self.aliases:
            return self.aliases[module_name]
        return module_name

    def load_module(self, module_name):  # pragma: no cover
        """ Loads module by name """
        try:
            module = import_module('SoftLayer.CLI.modules.%s' % module_name)
            for _, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, CLIRunnable):
                    self.add_plugin(obj)
            return module
        except ImportError:
            raise InvalidModule(module_name)

    def add_plugin(self, cls):
        """ Add a CLIRunnable as a plugin to the environment """
        command = cls.__module__.split('.')[-1]
        if command not in self.plugins:
            self.plugins[command] = {}
        self.plugins[command][cls.action] = cls

    def plugin_list(self):
        """ Returns the list of modules in SoftLayer.CLI.modules """
        return get_module_list()

    def out(self, output, newline=True):
        """ Outputs a string to the console (stdout) """
        self.stdout.write(output)
        if newline:
            self.stdout.write(os.linesep)

    def err(self, output, newline=True):
        """ Outputs an error string to the console (stderr) """
        self.stderr.write(output)
        if newline:
            self.stderr.write(os.linesep)

    def input(self, prompt):
        """ Provide a command prompt """
        return console_input(prompt)

    def getpass(self, prompt):
        """ Provide a password prompt """
        return getpass.getpass(prompt)

    def exit(self, code=0):
        """ Exit """
        sys.exit(code)


class CLIRunnable(object):
    """ CLIRunnable is intended to be subclassed. It represents a descrete
        command or action in the CLI. """
    options = []  # set by subclass
    action = 'not set'  # set by subclass

    def __init__(self, client=None, env=None):
        self.client = client
        self.env = env

    def execute(self, args):
        """ Execute the command. This is intended to be overridden in a
            subclass """
        pass
