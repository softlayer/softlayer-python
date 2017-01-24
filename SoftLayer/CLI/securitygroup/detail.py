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
    table.add_row(['name', secgroup.get('name', formatting.blank())])
    table.add_row(['description',
                   secgroup.get('description', formatting.blank())])

    rule_table = formatting.Table(['id', 'remoteIp', 'remoteGroupId',
                                   'direction', 'ethertype', 'portRangeMin',
                                   'portRangeMax', 'protocol'])
    for rule in secgroup.get('rules', []):
        rg_id = rule.get('remoteGroup', {}).get('id', formatting.blank())
        rule_table.add_row([rule['id'],
                            rule.get('remoteIp', formatting.blank()),
                            rule.get('remoteGroupId', rg_id),
                            rule['direction'],
                            rule.get('ethertype', formatting.blank()),
                            rule.get('portRangeMin', formatting.blank()),
                            rule.get('portRangeMax', formatting.blank()),
                            rule.get('protocol', formatting.blank())])

    table.add_row(['rules', rule_table])

    vsi_table = formatting.Table(['id', 'hostname', 'interface', 'ipAddress'])

    for binding in secgroup.get('networkComponentBindings'):
        vsi = binding['networkComponent']['guest']
        interface = ('PRIVATE' if binding['networkComponent']['port'] == 0
                     else 'PUBLIC')
        ip_address = (vsi['primaryBackendIpAddress']
                      if binding['networkComponent']['port'] == 0
                      else vsi['primaryIpAddress'])
        vsi_table.add_row([vsi['id'], vsi['hostname'], interface, ip_address])

    table.add_row(['servers', vsi_table])

    env.fout(table)
