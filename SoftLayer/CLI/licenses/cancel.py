"""Cancel a vwmare licenses."""
# :licenses: MIT, see LICENSE for more details.

import click
from SoftLayer import utils

from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.managers.license import LicensesManager


@click.command()
@click.argument('key')
@click.option('--immediate', is_flag=True, help='Immediate cancellation')
@environment.pass_env
def cli(env, key, immediate):
    """Cancel VMware licenses."""

    if not immediate:
        immediate = False
    vmware_find = False
    license = LicensesManager(env.client)

    vmware_licenses = license.get_all_objects()

    for vmware in vmware_licenses:
        if vmware.get('key') == key:
            vmware_find = True
            license.cancel_item(utils.lookup(vmware, 'billingItem', 'id'),
                                immediate,
                                'Cancel by cli command',
                                'Cancel by cli command')
            break

    if not vmware_find:
        raise exceptions.CLIAbort(
            "The VMware not found, try whit another key")
