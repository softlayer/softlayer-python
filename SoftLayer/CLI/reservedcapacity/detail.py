"""Display details for a specified reserved capacity."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer import utils


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Display details for a specified reserved capacity."""
    rcg_manager = SoftLayer.ReservedCapacityManager(env.client)
    rcg_id = helpers.resolve_id(rcg_manager.resolve_ids, identifier, 'Reserved Capacity')
    rcg_result = rcg_manager.detail(rcg_id)

    table = formatting.KeyValueTable(['Name', 'Value'], title="Reserved Capacity Detail")
    table.align['Name'] = 'r'
    table.align['Value'] = 'l'

    table.add_row(['name', utils.lookup(rcg_result, 'name')])
    table.add_row(['created', utils.lookup(rcg_result, 'createDate')])
    table.add_row(['location', utils.lookup(rcg_result, 'backendRouter', 'datacenter', 'longName')])
    table.add_row(['Pod', utils.lookup(rcg_result, 'backendRouter', 'hostname')])

    if not len(rcg_result['instances']) == 0:
        for instance in rcg_result['instances']:
            rcg_description = instance['billingItem']['description'].split("(")
            plan_terms = rcg_description[1].split(')')[0]
            profile = rcg_description[0]
            table.add_row(['plan terms', plan_terms])
            table.add_row(['profile', profile])

    instances_count_table = formatting.KeyValueTable(['Instances', 'Instances still available'])
    instances_count_table.add_row([rcg_result['occupiedInstanceCount'], rcg_result['availableInstanceCount']])
    table.add_row(['Capacity in use', instances_count_table])

    env.fout(table)
