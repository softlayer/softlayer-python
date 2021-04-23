"""Get details for a virtual server."""
# :license: MIT, see LICENSE for more details.

import logging

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer.CLI.virt.storage import get_local_storage_table
from SoftLayer import utils

LOGGER = logging.getLogger(__name__)


@click.command()
@click.argument('identifier')
@click.option('--passwords',
              is_flag=True,
              help='Show passwords (check over your shoulder!)')
@click.option('--price', is_flag=True, help='Show associated prices')
@environment.pass_env
def cli(env, identifier, passwords=False, price=False):
    """Get details for a virtual server."""

    vsi = SoftLayer.VSManager(env.client)
    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'

    vs_id = helpers.resolve_id(vsi.resolve_ids, identifier, 'VS')
    result = vsi.get_instance(vs_id)
    result = utils.NestedDict(result)
    local_disks = vsi.get_local_disks(vs_id)

    table_local_disks = get_local_storage_table(local_disks)

    table.add_row(['id', result['id']])
    table.add_row(['guid', result['globalIdentifier']])
    table.add_row(['hostname', result['hostname']])
    table.add_row(['domain', result['domain']])
    table.add_row(['fqdn', result['fullyQualifiedDomainName']])
    table.add_row(['status', formatting.FormattedItem(
        result['status']['keyName'],
        result['status']['name']
    )])
    table.add_row(['state', formatting.FormattedItem(
        utils.lookup(result, 'powerState', 'keyName'),
        utils.lookup(result, 'powerState', 'name'),
    )])
    table.add_row(['active_transaction', formatting.active_txn(result)])
    table.add_row(['datacenter', result['datacenter']['name'] or formatting.blank()])
    _cli_helper_dedicated_host(env, result, table)
    operating_system = utils.lookup(result,
                                    'operatingSystem',
                                    'softwareLicense',
                                    'softwareDescription') or {}
    table.add_row(['os', operating_system.get('name', '-')])
    table.add_row(['os_version', operating_system.get('version', '-')])
    table.add_row(['cores', result['maxCpu']])
    table.add_row(['memory', formatting.mb_to_gb(result['maxMemory'])])
    table.add_row(['drives', table_local_disks])
    table.add_row(['public_ip', result.get('primaryIpAddress', '-')])
    table.add_row(['private_ip', result.get('primaryBackendIpAddress', '-')])
    table.add_row(['private_only', result['privateNetworkOnlyFlag']])
    table.add_row(['private_cpu', result['dedicatedAccountHostOnlyFlag']])
    table.add_row(['transient', result.get('transientGuestFlag', False)])
    table.add_row(['created', result['createDate']])
    table.add_row(['modified', result['modifyDate']])
    last_transaction = "{} ({})".format(utils.lookup(result, 'lastTransaction', 'transactionGroup', 'name'),
                                        utils.clean_time(utils.lookup(result, 'lastTransaction', 'modifyDate')))

    table.add_row(['last_transaction', last_transaction])
    table.add_row(['billing', 'Hourly' if result['hourlyBillingFlag'] else'Monthly'])
    table.add_row(['preset', utils.lookup(result, 'billingItem',
                                          'orderItem',
                                          'preset',
                                          'keyName') or '-'])

    table.add_row(_get_owner_row(result))
    table.add_row(_get_vlan_table(result))

    bandwidth = vsi.get_bandwidth_allocation(vs_id)
    table.add_row(['Bandwidth', _bw_table(bandwidth)])

    security_table = _get_security_table(result)
    if security_table is not None:
        table.add_row(['security_groups', security_table])

    table.add_row(['notes', result.get('notes', '-')])

    if price:
        total_price = utils.lookup(result,
                                   'billingItem',
                                   'nextInvoiceTotalRecurringAmount') or 0
        total_price += sum(p['nextInvoiceTotalRecurringAmount']
                           for p
                           in utils.lookup(result,
                                           'billingItem',
                                           'children') or [])
        table.add_row(['price_rate', total_price])

    if passwords:
        pass_table = formatting.Table(['software', 'username', 'password'])

        for component in result['softwareComponents']:
            for item in component['passwords']:
                pass_table.add_row([
                    utils.lookup(component,
                                 'softwareLicense',
                                 'softwareDescription',
                                 'name'),
                    item['username'],
                    item['password'],
                ])

        table.add_row(['users', pass_table])

    table.add_row(['tags', formatting.tags(result['tagReferences'])])

    # Test to see if this actually has a primary (public) ip address
    try:
        if not result['privateNetworkOnlyFlag']:
            ptr_domains = env.client.call(
                'Virtual_Guest', 'getReverseDomainRecords',
                id=vs_id,
            )

            for ptr_domain in ptr_domains:
                for ptr in ptr_domain['resourceRecords']:
                    table.add_row(['ptr', ptr['data']])
    except SoftLayer.SoftLayerAPIError:
        pass

    env.fout(table)


def _bw_table(bw_data):
    """Generates a bandwidth useage table"""
    table = formatting.Table(['Type', 'In GB', 'Out GB', 'Allotment'])
    for bw_point in bw_data.get('usage'):
        bw_type = 'Private'
        allotment = 'N/A'
        if bw_point['type']['alias'] == 'PUBLIC_SERVER_BW':
            bw_type = 'Public'
            if not bw_data.get('allotment'):
                allotment = '-'
            else:
                allotment = utils.lookup(bw_data, 'allotment', 'amount')

        table.add_row([bw_type, bw_point['amountIn'], bw_point['amountOut'], allotment])
    return table


def _cli_helper_dedicated_host(env, result, table):
    """Get details on dedicated host for a virtual server."""

    dedicated_host_id = utils.lookup(result, 'dedicatedHost', 'id')
    if dedicated_host_id:
        table.add_row(['dedicated_host_id', dedicated_host_id])
        # Try to find name of dedicated host
        try:
            dedicated_host = env.client.call('Virtual_DedicatedHost', 'getObject',
                                             id=dedicated_host_id)
        except SoftLayer.SoftLayerAPIError:
            LOGGER.error('Unable to get dedicated host id %s', dedicated_host_id)
            dedicated_host = {}
        table.add_row(['dedicated_host',
                       dedicated_host.get('name') or formatting.blank()])


def _get_owner_row(result):
    """Formats and resturns the Owner row"""

    if utils.lookup(result, 'billingItem') != []:
        owner = utils.lookup(result, 'billingItem', 'orderItem', 'order', 'userRecord', 'username')
    else:
        owner = formatting.blank()
    return (['owner', owner])


def _get_vlan_table(result):
    """Formats and resturns a vlan table"""

    vlan_table = formatting.Table(['type', 'number', 'id'])
    for vlan in result['networkVlans']:
        vlan_table.add_row([
            vlan['networkSpace'], vlan['vlanNumber'], vlan['id']])
    return ['vlans', vlan_table]


def _get_security_table(result):
    secgroup_table = formatting.Table(['interface', 'id', 'name'])
    has_secgroups = False

    if result.get('networkComponents'):
        for comp in result.get('networkComponents'):
            interface = 'PRIVATE' if comp['port'] == 0 else 'PUBLIC'
            for binding in comp['securityGroupBindings']:
                has_secgroups = True
                secgroup = binding['securityGroup']
                secgroup_table.add_row([interface, secgroup['id'], secgroup.get('name', '-')])
    if has_secgroups:
        return secgroup_table
    else:
        return None
