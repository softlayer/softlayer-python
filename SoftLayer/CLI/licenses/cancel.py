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
    vm_ware_find = False
    licenses = LicensesManager(env.client)

    vm_ware_licenses = licenses.get_all_objects()

    for vm_ware in vm_ware_licenses:
        if vm_ware.get('key') == key:
            vm_ware_find = True
            licenses.cancel_item(utils.lookup(vm_ware, 'billingItem', 'id'),
                                immediate,
                                'Cancel by cli command',
                                'Cancel by cli command')
            break

    if not vm_ware_find:
        raise exceptions.CLIAbort(
            "The VMware not found, try whit another key")
