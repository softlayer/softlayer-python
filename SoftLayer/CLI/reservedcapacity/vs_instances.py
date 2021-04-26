"""List tickets."""
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
    """List the reserved capacity virtual server instances."""
    reserved_capacity_manager = SoftLayer.ReservedCapacityManager(env.client)
    reserved_capacity_id = helpers.resolve_id(reserved_capacity_manager.resolve_ids, identifier, 'Reserved Capacity')
    reserved_capacity_result = reserved_capacity_manager.vs_instances(reserved_capacity_id)

    guest_table = formatting.Table([
        'status', 'name', 'location', 'cpu', 'ram'
    ])

    for instance in reserved_capacity_result:
        if 'guest' in instance:
            ram = utils.lookup(instance, 'guest', 'maxMemory')
            ram_bytes = ram * (1024 ** 2)
            ram_result = ram_bytes / (1024 ** 3)
            guest_table.add_row([
                utils.lookup(instance, 'guest', 'status', 'name'),
                utils.lookup(instance, 'guest', 'fullyQualifiedDomainName'),
                utils.lookup(instance, 'guest', 'datacenter', 'longName'),
                utils.lookup(instance, 'guest', 'startCpus'),
                str(ram_result) + " GB",
            ])

    env.fout(guest_table)
