"""Cancel a license."""
# :licenses: MIT, see LICENSE for more details.

import click
import SoftLayer

from SoftLayer.CLI import environment


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('key')
@click.option('--immediate', is_flag=True, help='Immediate cancellation')
@environment.pass_env
def cli(env, key, immediate):
    """Cancel a license."""

    licenses = SoftLayer.LicensesManager(env.client)

    item = licenses.cancel_item(key, immediate)

    if item:
        env.fout("License key: {} was cancelled.".format(key))
