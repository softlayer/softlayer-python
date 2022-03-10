"""Get monitoring for a vSI device."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Get details for a vsi monitors device."""

    vsi = SoftLayer.VSManager(env.client)

    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'

    monitoring = vsi.get_instance(identifier)

    table.add_row(['domain', monitoring.get('fullyQualifiedDomainName')])
    table.add_row(['public Ip', monitoring.get('primaryIpAddress')])
    table.add_row(['private Ip', monitoring.get('primaryBackendIpAddress')])
    table.add_row(['location', monitoring['datacenter']['longName']])

    monitoring_table = formatting.Table(['Id', 'ipAddress', 'status', 'type', 'notify'])
    for monitor in monitoring['networkMonitors']:
        monitoring_table.add_row([monitor.get('id'), monitor.get('ipAddress'), monitor.get('status'),
                                  monitor['queryType']['name'], monitor['responseAction']['actionDescription']])

    table.add_row(['Devices monitors', monitoring_table])

    env.fout(table)
