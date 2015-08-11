"""Print environment variables."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@environment.pass_env
def cli(env):
    """Print environment variables."""
    return formatting.iter_to_table(env.vars)
