"""Exit the shell."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.shell import core


@click.command()
def cli():
    """Exit the shell."""
    raise core.ShellExit()
