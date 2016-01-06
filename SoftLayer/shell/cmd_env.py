"""Print environment variables."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@environment.pass_env
def cli(env):
    """Print environment variables."""
    filtered_vars = dict([(k, v)
                          for k, v in env.vars.items()
                          if not k.startswith('_')])
    env.fout(formatting.iter_to_table(filtered_vars))
