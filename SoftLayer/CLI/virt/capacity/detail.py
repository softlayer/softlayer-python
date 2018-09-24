"""Shows the details of a reserved capacity group"""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.vs_capacity import CapacityManager as CapacityManager


from pprint import pprint as pp

@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Reserved Capacity Group Details"""
    manager = CapacityManager(env.client)
    result = manager.get_object(identifier)
    try:
        flavor = result['instances'][0]['billingItem']['description']
    except KeyError:
        flavor = "Pending Approval..."

    table = formatting.Table(
        ["ID", "Created"], 
        title= "%s - %s" % (result.get('name'), flavor)
    )
    for rci in result['instances']:
        table.add_row([rci['guestId'], rci['createDate']])
    env.fout(table)

