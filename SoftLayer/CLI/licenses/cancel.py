"""Cancel a license."""
# :licenses: MIT, see LICENSE for more details.

import click
import SoftLayer

from SoftLayer.CLI import environment


@click.command()
@click.argument('key')
@click.option('--immediate', is_flag=True, help='Immediate cancellation')
@environment.pass_env
def cli(env, key, immediate):
    """Cancel a license."""

    licenses = SoftLayer.LicensesManager(env.client)

    env.fout(licenses.cancel_item(key, immediate))
