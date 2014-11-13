"""Show current CLI configuration."""
# :license: MIT, see LICENSE for more details.

from softlayer.cli import config
from softlayer.cli import environment

import click


@click.command()
@environment.pass_env
def cli(env):
    """Show current configuration."""

    settings = config.get_settings_from_client(env.client)
    return config.config_table(settings)
