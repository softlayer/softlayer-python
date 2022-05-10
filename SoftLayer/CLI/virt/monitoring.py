"""Get monitoring for a VSI device."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Get details for a vsi monitors device."""

    vsi = SoftLayer.VSManager(env.client)

    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'

    monitoring = vsi.get_instance(identifier)

    table.add_row(['Domain', monitoring.get('fullyQualifiedDomainName')])
    table.add_row(['Public Ip', monitoring.get('primaryIpAddress')])
    table.add_row(['Private Ip', monitoring.get('primaryBackendIpAddress')])
    table.add_row(['Location', monitoring['datacenter']['longName']])

    monitoring_table = formatting.Table(['Id', 'IpAddress', 'Status', 'Type', 'Notify'])
    for monitor in monitoring['networkMonitors']:
        monitoring_table.add_row([monitor.get('id'), monitor.get('ipAddress'), monitor.get('status'),
                                  monitor['queryType']['name'], monitor['responseAction']['actionDescription']])

    table.add_row(['Devices monitors', monitoring_table])

    env.fout(table)
