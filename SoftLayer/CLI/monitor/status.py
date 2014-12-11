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
        'id', 'datacenter', 'FQDN', 'IP',
        'status', 'Type', 'last checked at'
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
    for serverObject in results:
        server = utils.NestedDict(serverObject)
        for monitor in server['networkMonitors']:
            res = monitor['lastResult']['responseStatus']
            date = monitor['lastResult']['finishTime']
            ip = monitor['ipAddress']
            monitorType = monitor['queryType']['name']
            status = 'UNKNOWN'
            status_color = None
            if res == 0:
                status = 'DOWN'
                status_color = 'red'
            elif res == 1:
                status = 'WARNING'
                status_color = 'yellow'
            elif res == 2:
                status = 'OK'
                status_color = 'green'

            table.add_row([
                server['id'],
                server['datacenter']['name'] or formatting.blank(),
                server['fullyQualifiedDomainName'],
                ip or formatting.blank(),
                click.style(status, fg=status_color),
                monitorType,
                date 
            ])

    return table
