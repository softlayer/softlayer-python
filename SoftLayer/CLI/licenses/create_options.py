"""Licenses order options for a given VMware licenses."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI.command import SLCommand as SLCommand
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.licenses import LicensesManager
from SoftLayer import utils


@click.command(cls=SLCommand)
@environment.pass_env
def cli(env):
    """Server order options for a given chassis."""

    licenses_manager = LicensesManager(env.client)

    options = licenses_manager.get_create_options()

    table = formatting.Table(['Id', 'description', 'keyName', 'capacity', 'recurringFee'])
    for item in options:
        fee = 0
        if len(item.get('prices', [])) > 0:
            fee = item.get('prices')[0].get('recurringFee', 0)
        table.add_row([item.get('id'),
                       utils.trim_to(item.get('description'), 40),
                       item.get('keyName'),
                       item.get('capacity'),
                       fee])

    env.fout(table)
