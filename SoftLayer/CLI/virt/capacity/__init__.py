"""Manages Reserved Capacity."""
# :license: MIT, see LICENSE for more details.

import importlib
import os

import click

CONTEXT = {'help_option_names': ['-h', '--help'],
           'max_content_width': 999}


class CapacityCommands(click.MultiCommand):
    """Loads module for capacity related commands.

    Will automatically replace _ with - where appropriate.
    I'm not sure if this is better or worse than using a long list of manual routes, so I'm trying it here.
    CLI/virt/capacity/create_guest.py -> slcli vs capacity create-guest
    """

    def __init__(self, **attrs):
        click.MultiCommand.__init__(self, **attrs)
        self.path = os.path.dirname(__file__)

    def list_commands(self, ctx):
        """List all sub-commands."""
        commands = []
        for filename in os.listdir(self.path):
            if filename == '__init__.py':
                continue
            if filename.endswith('.py'):
                commands.append(filename[:-3].replace("_", "-"))
        commands.sort()
        return commands

    def get_command(self, ctx, cmd_name):
        """Get command for click."""
        path = "%s.%s" % (__name__, cmd_name)
        path = path.replace("-", "_")
        module = importlib.import_module(path)
        return getattr(module, 'cli')


# Required to get the sub-sub-sub command to work.
@click.group(cls=CapacityCommands, context_settings=CONTEXT)
def cli():
    """Base command for all capacity related concerns"""
    pass
