"""List billing information of orders."""
# :license: MIT, see LICENSE for more details.


import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils

import click


@click.command()
@click.option('--start_date', '-f', help='cost incurred from this start date')
@click.option('--end_date', '-e',
              help='cost incurred before this end date'
                   ' (default is current time stamp)')
@environment.pass_env
def cli(env, start_date, end_date):
    """List billing information for orders."""
    billing = SoftLayer.BillingManager(env.client)
    from_date = start_date
    to_date = end_date
    table = formatting.Table(['Order ID', 'Resource Name', 'Resource Type',
                              'cost', 'create_date'])
    resources = billing.list_resources(from_date, to_date)

    for resource in resources:
        resource = utils.NestedDict(resource)
        table.add_row([
            resource['id'],
            resource['hostName'],
            resource['resourceType'],
            resource['cost'],
            resource['createDate']
        ])

    return table
