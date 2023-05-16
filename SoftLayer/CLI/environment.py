"""
    SoftLayer.CLI.environment
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    Abstracts everything related to the user's environment when running the CLI

    :license: MIT, see LICENSE for more details.
"""
import configparser
import os

import importlib
from json.decoder import JSONDecodeError

import click
import pkg_resources
from rich.console import Console
from rich.syntax import Syntax

import SoftLayer
from SoftLayer.CLI import formatting
from SoftLayer.CLI import routes
from SoftLayer import utils

# pylint: disable=too-many-instance-attributes, invalid-name

# Calling pkg_resources.iter_entry_points shows a false-positive
# pylint: disable=no-member


class Environment(object):
    """Provides access to the current CLI environment."""

    def __init__(self):
        # {'path:to:command': ModuleLoader()}
        # {'vs:list': ModuleLoader()}
        self.commands = {}
        self.aliases = {}

        self.vars = {}

        self.client = None
        self.theme = self.set_env_theme()
        self.console = utils.console_color_themes(self.theme)
        self.err_console = Console(stderr=True)
        self.format = 'table'
        self.skip_confirmations = False
        self.config_file = None

        self._modules_loaded = False

    def out(self, output):
        """Outputs a string to the console (stdout)."""

        # If we output to a | or file, need to set default width so all output is printed.
        if not self.console.is_terminal:
            self.console.width = 1000000
        if self.format == 'json':
            try:
                self.console.print_json(output)
            # Tried to print not-json, so just print it out normally...
            except JSONDecodeError:
                click.echo(output)
        elif self.format == 'jsonraw':
            #  Using Rich here is problematic because in the unit tests it thinks the terminal is 80 characters wide
            #  and only prints out that many characters.
            click.echo(output)
        else:
            # If we want to print a list of tables, Rich doens't handle that well.
            if isinstance(output, list):
                for line in output:
                    self.console.print(line, overflow='ignore')
            else:
                self.console.print(output,  overflow='ignore')

    def err(self, output, newline=True):
        """Outputs an error string to the console (stderr)."""

        self.err_console.print(output, new_line_start=newline)

    def fmt(self, output, fmt=None):
        """Format output based on current the environment format."""
        if fmt is None:
            fmt = self.format
        return formatting.format_output(output, fmt, self.theme)

    def format_output_is_json(self):
        """Return True if format output is json or jsonraw"""
        return 'json' in self.format

    def fout(self, output):
        """Format the input and output to the console (stdout)."""
        if output is not None:
            try:
                self.out(self.fmt(output))
            except UnicodeEncodeError:
                # If we hit an undecodeable entry, just try outputting as json.
                self.out(self.fmt(output, 'json'))

    def python_output(self, output):
        """Prints out python code"""
        self.console.print(Syntax(output, "python"))

    def input(self, prompt, default=None, show_default=True):
        """Provide a command prompt."""
        return click.prompt(prompt, default=default, show_default=show_default)

    def getpass(self, prompt, default=None):
        """Provide a password prompt."""
        password = click.prompt(prompt, hide_input=True, default=default)

        # https://github.com/softlayer/softlayer-python/issues/1436
        # click.prompt uses python's getpass() in the background
        # https://github.com/python/cpython/blob/3.9/Lib/getpass.py#L97
        # In windows, shift+insert actually inputs the below 2 characters
        # If we detect those 2 characters, need to manually read from the clipbaord instead
        # https://stackoverflow.com/questions/101128/how-do-i-read-text-from-the-clipboard
        if password == 'àR':
            # tkinter is a built in python gui, but it has clipboard reading functions.
            # pylint: disable=import-outside-toplevel
            from tkinter import Tk
            tk_manager = Tk()
            password = tk_manager.clipboard_get()
            # keep the window from showing
            tk_manager.withdraw()
        return password

    # Command loading methods
    def list_commands(self, *path):
        """Command listing."""
        path_str = ':'.join(path)

        commands = []
        for command in self.commands:

            # Filter based on prefix and the segment length
            if all([command.startswith(path_str),
                    len(path) == command.count(":")]):

                # offset is used to exclude the path that the caller requested.
                offset = len(path_str) + 1 if path_str else 0
                if ':' not in command[offset:]:
                    commands.append(command[offset:])

        return sorted(commands)

    def get_command(self, *path):
        """Return command at the given path or raise error."""
        path_str = ':'.join(path)

        if path_str in self.commands:
            return self.commands[path_str].load()

        return None

    def resolve_alias(self, path_str):
        """Returns the actual command name. Uses the alias mapping."""
        if path_str in self.aliases:
            return self.aliases[path_str]
        return path_str

    def load(self):
        """Loads all modules."""
        if self._modules_loaded is True:
            return

        self.load_modules_from_python(routes.ALL_ROUTES)
        self.aliases.update(routes.ALL_ALIASES)
        self._load_modules_from_entry_points('softlayer.cli')

        self._modules_loaded = True

    def load_modules_from_python(self, route_list):
        """Load modules from the native python source."""
        for name, modpath in route_list:
            if ':' in modpath:
                path, attr = modpath.split(':', 1)
            else:
                path, attr = modpath, None
            self.commands[name] = ModuleLoader(path, attr=attr)

    def _load_modules_from_entry_points(self, entry_point_group):
        """Load modules from the entry_points (slower).

        Entry points can be used to add new commands to the CLI.

        Usage:

            entry_points={'softlayer.cli': ['new-cmd = mymodule.new_cmd.cli']}

        """
        for obj in pkg_resources.iter_entry_points(group=entry_point_group,
                                                   name=None):
            self.commands[obj.name] = obj

    def ensure_client(self, config_file=None, is_demo=False, proxy=None):
        """Create a new SLAPI client to the environment.

        This will be a no-op if there is already a client in this environment.
        """
        if self.client is not None:
            return

        # Environment can be passed in explicitly. This is used for testing
        if is_demo:
            client = SoftLayer.BaseClient(
                transport=SoftLayer.FixtureTransport(),
                auth=None,
            )
        else:
            # Create SL Client
            client = SoftLayer.create_client_from_env(
                proxy=proxy,
                config_file=config_file,
            )
        self.client = client

    def set_env_theme(self, config_file=None):
        """Get theme to color console and set in env"""
        theme = os.environ.get('SL_THEME')
        if theme:
            return theme
        else:
            config_files = ['/etc/softlayer.conf', '~/.softlayer']
            path_os = os.getenv('HOME')
            if path_os:
                config_files.append(path_os + '\\AppData\\Roaming\\softlayer')
            if config_file:
                config_files.append(config_file)
            config = configparser.RawConfigParser({'theme': 'dark'})
            config.read(config_files)
            if config.has_section('softlayer'):
                self.theme = config.get('softlayer', 'theme')
                return config.get('softlayer', 'theme')
        return 'dark'


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
