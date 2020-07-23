"""Lists the Virtual Guests running on this server."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer import utils


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Lists the Virtual Guests running on this server."""

    mgr = SoftLayer.HardwareManager(env.client)
    hw_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'hardware')
    hw_guests = mgr.get_hardware_guests(hw_id)

    if not hw_guests:
        raise exceptions.CLIAbort("No Virtual Guests found.")

    table = formatting.Table(['id', 'hostname', 'CPU', 'Memory', 'Start Date', 'Status', 'powerState'])
    table.sortby = 'hostname'
    for guest in hw_guests:
        table.add_row([
            guest['id'],
            guest['hostname'],
            '%i %s' % (guest['maxCpu'], guest['maxCpuUnits']),
            guest['maxMemory'],
            utils.clean_time(guest['createDate']),
            guest['status']['keyName'],
            guest['powerState']['keyName']
        ])

    env.fout(table)
