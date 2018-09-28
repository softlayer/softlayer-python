"""Manages Reserved Capacity."""
# :license: MIT, see LICENSE for more details.
import importlib
import click
import types
import SoftLayer
import os
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting

from pprint import pprint as pp
CONTEXT = {'help_option_names': ['-h', '--help'],
           'max_content_width': 999}
class capacityCommands(click.MultiCommand):
    """Loads module for capacity related commands."""

    def __init__(self, *path, **attrs):
        click.MultiCommand.__init__(self, **attrs)
        self.path = os.path.dirname(__file__)

    def list_commands(self, ctx):
        """List all sub-commands."""
        rv = []
        for filename in os.listdir(self.path):
            if filename == '__init__.py':
                continue
            if filename.endswith('.py'):
                rv.append(filename[:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        """Get command for click."""
        path = "%s.%s" % (__name__, name)
        module = importlib.import_module(path)
        return getattr(module, 'cli')

@click.group(cls=capacityCommands,
             context_settings=CONTEXT)
@environment.pass_env
def cli(env):
    """Manages Reserved Capacity"""
    pass
