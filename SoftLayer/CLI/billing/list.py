"""List BIlling information of Accounts."""
# :license: MIT, see LICENSE for more details.


import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils

import click


@click.command()
@click.option('--frmdate', '-f', help='cost incurred from from_date')
@click.option('--enddate', '-e',
              help='end date to consider, default is latest time stamp')
@click.option('--group', '-g',
              help='grouping by a resource type e.g server, iscsi etc.')
@click.option('--resource', '-r',
              help='shows only cost of the active/inactive resources',
              type=click.Choice(['active',
                                 'inactive']))
@environment.pass_env
def cli(env, frmdate, enddate, group, resource):
    """List billing information for accounts."""
    billing = SoftLayer.BillingManager(env.client)
    from_date = frmdate
    to_date = enddate
    group_by = group
    resource_status = resource
    table = formatting.Table(['Order ID', 'Resource Name', 'Resource Type',
                   'cost', 'create_date'])
    result = billing.list_resources(from_date, to_date, group_by)


    return table
