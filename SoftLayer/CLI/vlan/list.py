"""List VLANs."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI.vlan.detail import get_gateway_firewall
from SoftLayer import utils

COLUMNS = ['Id',
           'Number',
           'Fully qualified name',
           'Name',
           'Network',
           'Data center',
           'Pod',
           'Gateway/Firewall',
           'Hardware',
           'Virtual servers',
           'Public ips',
           'Premium',
           'Tags']


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.option('--sortby',
              help='Column to sort by',
              type=click.Choice(COLUMNS))
@click.option('--datacenter', '-d',
              help='Filter by datacenter shortname (sng01, dal05, ...)')
@click.option('--number', '-n', help='Filter by VLAN number')
@click.option('--name', help='Filter by VLAN name')
@click.option('--limit', '-l',
              help='How many results to get in one api call, default is 100',
              default=100,
              show_default=True)
@environment.pass_env
def cli(env, sortby, datacenter, number, name, limit):
    """List VLANs.

    Note: A * Indicates a POD is closing soon. Ex:[red] Pod01* [/red]
    """

    mgr = SoftLayer.NetworkManager(env.client)

    table = formatting.Table(COLUMNS)
    table.sortby = sortby

    vlans = mgr.list_vlans(datacenter=datacenter,
                           vlan_number=number,
                           name=name,
                           limit=limit)

    mask = """mask[name, datacenterLongName, frontendRouterId, capabilities, datacenterId, backendRouterId,
                    backendRouterName, frontendRouterName]"""
    pods = mgr.get_pods(mask=mask)

    for vlan in vlans:
        billing = 'Yes' if vlan.get('billingItem') else 'No'

        table.add_row([
            vlan.get('id'),
            vlan.get('vlanNumber'),
            vlan.get('fullyQualifiedName'),
            vlan.get('name') or formatting.blank(),
            vlan.get('networkSpace', 'Direct Link').capitalize(),
            utils.lookup(vlan, 'primaryRouter', 'datacenter', 'name'),
            get_pod_with_closed_announcement(vlan, pods),
            get_gateway_firewall(vlan),
            vlan.get('hardwareCount'),
            vlan.get('virtualGuestCount'),
            vlan.get('totalPrimaryIpAddressCount'),
            billing,
            formatting.tags(vlan['tagReferences'])
        ])

    env.fout(table)


def get_pod_with_closed_announcement(vlan, pods):
    """Gets pods with announcement to close"""
    for pod in pods:
        if utils.lookup(pod, 'backendRouterId') == utils.lookup(vlan, 'primaryRouter', 'id') \
                or utils.lookup(pod, 'frontendRouterId') == utils.lookup(vlan, 'primaryRouter', 'id'):
            if 'CLOSURE_ANNOUNCED' in utils.lookup(pod, 'capabilities'):
                name_pod = utils.lookup(pod, 'name').split('.')[1] + '*'
                return "[red]" + name_pod.capitalize() + "[/red]"
            else:
                return utils.lookup(pod, 'name').split('.')[1].capitalize()
    return ''
