"""Get details about a security group."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Get details about a security group."""

    mgr = SoftLayer.NetworkManager(env.client)

    secgroup = mgr.get_securitygroup(identifier)

    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'

    table.add_row(['id', secgroup['id']])
    table.add_row(['name', secgroup.get('name') or formatting.blank()])
    table.add_row(['description',
                   secgroup.get('description') or formatting.blank()])

    rule_table = formatting.Table(['id', 'remoteIp', 'remoteGroupId',
                                   'direction', 'ethertype', 'portRangeMin',
                                   'portRangeMax', 'protocol'])
    for rule in secgroup.get('rules', []):
        rg_id = rule.get('remoteGroup', {}).get('id') or formatting.blank()
        port_min = rule.get('portRangeMin')
        port_max = rule.get('portRangeMax')
        if port_min is None:
            port_min = formatting.blank()
        if port_max is None:
            port_max = formatting.blank()
        rule_table.add_row([rule['id'],
                            rule.get('remoteIp') or formatting.blank(),
                            rule.get('remoteGroupId', rg_id),
                            rule['direction'],
                            rule.get('ethertype') or formatting.blank(),
                            port_min,
                            port_max,
                            rule.get('protocol') or formatting.blank()])

    table.add_row(['rules', rule_table])

    vsi_table = formatting.Table(['id', 'hostname', 'interface', 'ipAddress'])

    for binding in secgroup.get('networkComponentBindings', []):
        try:
            vsi = binding['networkComponent']['guest']
            vsi_id = vsi['id']
            hostname = vsi['hostname']
            interface = ('PRIVATE' if binding['networkComponent']['port'] == 0
                         else 'PUBLIC')
            ip_address = (vsi['primaryBackendIpAddress']
                          if binding['networkComponent']['port'] == 0
                          else vsi['primaryIpAddress'])
        except KeyError:
            vsi_id = "N/A"
            hostname = "Not enough permission to view"
            interface = "N/A"
            ip_address = "N/A"
        vsi_table.add_row([vsi_id, hostname, interface, ip_address])

    table.add_row(['servers', vsi_table])

    env.fout(table)
