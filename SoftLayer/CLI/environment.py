"""
    SoftLayer.CLI.environment
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    Abstracts everything related to the user's environment when running the CLI

    :license: MIT, see LICENSE for more details.
"""
import getpass
import importlib
import sys

from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import modules
from SoftLayer import utils

import click
import pkg_resources

# pylint: disable=too-many-instance-attributes, invalid-name


class Environment(object):
    """Provides access to the current CLI environment."""
    def __init__(self):
        # {'module_name': {'action': plugin_loader}}
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
        self.client = None
        self.format = 'table'
        self.skip_confirmations = False
        self._modules_loaded = False
        self.config_file = None

    def command_list(self, module_name):
        """Command listing"""

        self._load_modules()
        # Filter commands registered as None. These are the bases.
        return sorted([m for m in self.plugins[module_name].keys()
                       if m is not None])

    def module_list(self):
        """Returns the list of modules in SoftLayer.CLI.modules."""
        self._load_modules()
        return sorted(list(self.plugins.keys()))

    def get_command(self, module_name, command_name):
        """Based on the loaded modules, return a command."""
        self._load_modules()
        actions = self.plugins.get(module_name) or {}

        if command_name in actions:
            return actions[command_name].load()

        raise exceptions.InvalidCommand(module_name, command_name)

    def get_module(self, module_name):
        """Returns the module"""
        self._load_modules()
        return self.get_command(module_name, None)

    def get_module_name(self, module_name):
        """Returns the actual module name. Uses the alias mapping."""
        if module_name in self.aliases:
            return self.aliases[module_name]
        return module_name

    def _load_modules(self):
        """Loads all modules."""
        if self._modules_loaded is True:
            return

        self._load_modules_from_python()
        self._load_modules_from_entry_points()

        self._modules_loaded = True

    def _load_modules_from_python(self):
        """Load modules from the native python source."""
        for name, modpath in modules.ALL_MODULES:
            module, subcommand = _parse_name(name)
            if module not in self.plugins:
                self.plugins[module] = {}

            if ':' in modpath:
                path, attr = modpath.split(':', 1)
            else:
                path, attr = modpath, None
            self.plugins[module][subcommand] = ModuleLoader(path, attr=attr)

    def _load_modules_from_entry_points(self):
        """Load modules from the entry_points (slower)."""
        for obj in pkg_resources.iter_entry_points(group='softlayer.cli',
                                                   name=None):

            module, subcommand = _parse_name(obj.name)
            if module not in self.plugins:
                self.plugins[module] = {}
            self.plugins[module][subcommand] = obj

    def out(self, output, newline=True):
        """Outputs a string to the console (stdout)."""
        click.echo(output, nl=newline)

    def err(self, output, newline=True):
        """Outputs an error string to the console (stderr)."""
        click.echo(output, nl=newline, err=True)

    def fmt(self, output):
        """Format output based on current the environment format"""
        return formatting.format_output(output, fmt=self.format)

    def input(self, prompt):
        """Provide a command prompt."""
        return utils.console_input(prompt)

    def getpass(self, prompt):
        """Provide a password prompt."""
        return getpass.getpass(prompt)

    def exit(self, code=0):
        """Exit."""
        sys.exit(code)


class ModuleLoader(object):
    """Module loader that acts a little like an EntryPoint object."""

    def __init__(self, import_path, attr=None):
        self.import_path = import_path
        self.attr = attr

    def load(self):
        """load and return the module/attribute"""
        module = importlib.import_module(self.import_path)
        if self.attr:
            return getattr(module, self.attr)
        return module


def _parse_name(name):
    """Parse command name and path from the given name."""
    if ':' in name:
        module, subcommand = name.split(':', 1)
    else:
        module, subcommand = name, None

    return module, subcommand


pass_env = click.make_pass_decorator(Environment, ensure=True)
