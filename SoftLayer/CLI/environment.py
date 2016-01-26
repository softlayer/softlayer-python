"""
    SoftLayer.CLI.environment
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    Abstracts everything related to the user's environment when running the CLI

    :license: MIT, see LICENSE for more details.
"""
import importlib

import click
import pkg_resources

import SoftLayer
from SoftLayer.CLI import formatting
from SoftLayer.CLI import routes

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

        self.vars = {}

        self.client = None
        self.format = 'table'
        self.skip_confirmations = False
        self.config_file = None

        self._modules_loaded = False

    def out(self, output, newline=True):
        """Outputs a string to the console (stdout)."""
        click.echo(output, nl=newline)

    def err(self, output, newline=True):
        """Outputs an error string to the console (stderr)."""
        click.echo(output, nl=newline, err=True)

    def fmt(self, output):
        """Format output based on current the environment format."""
        return formatting.format_output(output, fmt=self.format)

    def fout(self, output, newline=True):
        """Format the input and output to the console (stdout)."""
        if output is not None:
            self.out(self.fmt(output), newline=newline)

    def input(self, prompt, default=None, show_default=True):
        """Provide a command prompt."""
        return click.prompt(prompt, default=default, show_default=show_default)

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
                offset = len(path_str) + 1 if path_str else 0
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
