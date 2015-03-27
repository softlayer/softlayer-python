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
    hw_manager = SoftLayer.HardwareMonitorManager(env.client)
    vs_manager = SoftLayer.VSMonitorManager(env.client)
    if only_virtual:
        hardware = []
        guest = vs_manager.list_status()
    elif only_hardware:
        hardware = hw_manager.list_status()
        guest = []
    else:
        hardware = hw_manager.list_status()
        guest = vs_manager.list_status()

    results = hardware + guest
    for server_object in results:
        server = utils.NestedDict(server_object)
        for monitor in server['networkMonitors']:
            try:
                res = monitor['lastResult']['responseStatus']
                date = monitor['lastResult']['finishTime']
                ip_address = monitor['ipAddress']
                monitor_type = monitor['queryType']['name']
            except KeyError:
                # if a monitor does't have the lastResult ususally it is
                # still being provisioned
                res = 0
                date = "--"
                ip_address = None
                monitor_type = "--"

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
                ip_address or formatting.blank(),
                click.style(status, fg=status_color),
                monitor_type,
                date
            ])

    return table
