"""List all global IPs."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@click.option('--ip-version',
              help='Display only IPv4',
              type=click.Choice(['v4', 'v6']))
@environment.pass_env
def cli(env, ip_version):
    """List all global IPs."""

    mgr = SoftLayer.NetworkManager(env.client)

    table = formatting.Table(['id', 'ip', 'assigned', 'target'])

    version = None
    if ip_version == 'v4':
        version = 4
    elif ip_version == 'v6':
        version = 6

    ips = mgr.list_global_ips(version=version)

    for ip_address in ips:
        assigned = 'No'
        target = 'None'
        if ip_address.get('destinationIpAddress'):
            dest = ip_address['destinationIpAddress']
            assigned = 'Yes'
            target = dest['ipAddress']
            virtual_guest = dest.get('virtualGuest')
            if virtual_guest:
                target += (' (%s)'
                           % virtual_guest['fullyQualifiedDomainName'])
            elif ip_address['destinationIpAddress'].get('hardware'):
                target += (' (%s)'
                           % dest['hardware']['fullyQualifiedDomainName'])

        table.add_row([ip_address['id'],
                       ip_address['ipAddress']['ipAddress'],
                       assigned,
                       target])
    env.fout(table)
