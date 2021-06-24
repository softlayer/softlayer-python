"""Order/create a vwmare licenses."""
# :licenses: MIT, see LICENSE for more details.

import click

import SoftLayer

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@click.option('--key', '-k', required=True, prompt=True,
              help="The VMware License Key. "
                   "To get could use the product_package::getItems id=301 with name Software License Package"
                   "E.g VMWARE_VSAN_ENTERPRISE_TIER_III_65_124_TB_6_X_2")
@click.option('--datacenter', '-d', required=True, prompt=True, help="Datacenter shortname")
@environment.pass_env
def cli(env, key, datacenter):
    """Order/Create License."""

    item_package = [key]

    licenses = SoftLayer.LicensesManager(env.client)

    result = licenses.create(datacenter, item_package)

    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'
    table.add_row(['id', result['orderId']])
    table.add_row(['created', result['orderDate']])

    env.fout(table)
