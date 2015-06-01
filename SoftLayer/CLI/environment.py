"""
    SoftLayer.CLI.environment
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    Abstracts everything related to the user's environment when running the CLI

    :license: MIT, see LICENSE for more details.
"""
import importlib

from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import routes

import click
import pkg_resources

# pylint: disable=too-many-instance-attributes, invalid-name, no-self-use

# Calling pkg_resources.iter_entry_points shows a false-positive
# pylint: disable=no-member


class Environment(object):
    """Provides access to the current CLI environment."""

    def __init__(self):
        # {'path:to:command': ModuleLoader()}
        # {'vs:list': ModuleLoader()}
        self.commands = {}
        self.aliases = {}

        self.client = None
        self.format = 'table'
        self.skip_confirmations = False
        self._modules_loaded = False
        self.config_file = None

    def out(self, output, newline=True):
        """Outputs a string to the console (stdout)."""
        click.echo(output, nl=newline)

    def err(self, output, newline=True):
        """Outputs an error string to the console (stderr)."""
        click.echo(output, nl=newline, err=True)

    def fmt(self, output):
        """Format output based on current the environment format."""
        return formatting.format_output(output, fmt=self.format)

    def input(self, prompt, default=None):
        """Provide a command prompt."""
        return click.prompt(prompt, default=default)

    def getpass(self, prompt, default=None):
        """Provide a password prompt."""
        return click.prompt(prompt, hide_input=True, default=default)

    # Command loading methods
    def list_commands(self, *path):
        """Command listing."""
        path_str = ':'.join(path)

        commands = []
        for command in self.commands.keys():

            # Filter based on prefix and the segment length
            if all([command.startswith(path_str),
                    len(path) == command.count(":")]):

                # offset is used to exclude the path that the caller requested.
                offset = len(path_str)+1 if path_str else 0
                commands.append(command[offset:])

        return sorted(commands)

    def get_command(self, *path):
        """Return command at the given path or raise error."""
        path_str = ':'.join(path)

        if path_str in self.commands:
            return self.commands[path_str].load()

        raise exceptions.InvalidCommand(path)

    def resolve_alias(self, path_str):
        """Returns the actual command name. Uses the alias mapping."""
        if path_str in self.aliases:
            return self.aliases[path_str]
        return path_str

    def load(self):
        """Loads all modules."""
        if self._modules_loaded is True:
            return

        self._load_modules_from_python()
        self._load_modules_from_entry_points()

        self._modules_loaded = True

    def _load_modules_from_python(self):
        """Load modules from the native python source."""
        for name, modpath in routes.ALL_ROUTES:
            if ':' in modpath:
                path, attr = modpath.split(':', 1)
            else:
                path, attr = modpath, None
            self.commands[name] = ModuleLoader(path, attr=attr)

        self.aliases = routes.ALL_ALIASES

    def _load_modules_from_entry_points(self):
        """Load modules from the entry_points (slower).

        Entry points can be used to add new commands to the CLI.

        Usage:

            entry_points={'softlayer.cli': ['new-cmd = mymodule.new_cmd.cli']}

        """
        for obj in pkg_resources.iter_entry_points(group='softlayer.cli',
                                                   name=None):
            self.commands[obj.name] = obj


class ModuleLoader(object):
    """Module loader that acts a little like an EntryPoint object."""

    def __init__(self, import_path, attr=None):
        self.import_path = import_path
        self.attr = attr

    def load(self):
        """load and return the module/attribute."""
        module = importlib.import_module(self.import_path)
        if self.attr:
            return getattr(module, self.attr)
        return module


pass_env = click.make_pass_decorator(Environment, ensure=True)
