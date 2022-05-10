"""Show current CLI configuration."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI.command import SLCommand as SLCommand
from SoftLayer.CLI import config
from SoftLayer.CLI import environment


@click.command(cls=SLCommand)
@environment.pass_env
def cli(env):
    """Show current configuration."""

    settings = config.get_settings_from_client(env.client)
    env.fout(config.config_table(settings))
