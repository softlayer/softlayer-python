"""
usage: sl monitor [<command>] [<args>...] [options]

Manage Monitoring.

The available commands are:
    status  Show basic monitoring status of servers
"""

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils


@click.command()
@click.option('--only_hardware', is_flag=True,
              help="Show only physical servers")
@click.option('--only_virtual', is_flag=True,
              help="Show only virtual servers")
@environment.pass_env
def cli(env, only_hardware=False, only_virtual=False):
    """shows SERVER_PING status of all servers."""

    table = formatting.Table([
        'id', 'datacenter', 'FQDN', 'public ip',
        'status', 'last checked at'
    ])

    manager = SoftLayer.MonitoringManager(env.client)
    if only_virtual:
        hardware = []
        guest = manager.list_guest_status()
    elif only_hardware:
        hardware = manager.list_hardware_status()
        guest = []
    else:
        hardware = manager.list_hardware_status()
        guest = manager.list_guest_status()

    results = hardware + guest
    for server in results:
        server = utils.NestedDict(server)
        res = server['networkMonitors'][0]['lastResult']['responseStatus']
        date = server['networkMonitors'][0]['lastResult']['finishTime']
        status = '\033[35mUNKNOWN\033[0m'
        if res == 0:
            status = '\033[31mDOWN\033[0m'
        elif res == 1:
            status = '\033[93mWARNING\033[0m'
        elif res == 2:
            status = '\033[32mOK\033[0m'

        table.add_row([
            server['id'],
            server['datacenter']['name'] or formatting.blank(),
            server['fullyQualifiedDomainName'],
            server['primaryIpAddress'] or formatting.blank(),
            status,
            date
        ])

    return table
