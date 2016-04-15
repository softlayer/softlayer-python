"""Get details for a virtual server."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer import utils


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

    table.add_row(['id', result['id']])
    table.add_row(['guid', result['globalIdentifier']])
    table.add_row(['hostname', result['hostname']])
    table.add_row(['domain', result['domain']])
    table.add_row(['fqdn', result['fullyQualifiedDomainName']])
    table.add_row(['status', formatting.FormattedItem(
        result['status']['keyName'] or formatting.blank(),
        result['status']['name'] or formatting.blank()
    )])
    table.add_row(['state', formatting.FormattedItem(
        utils.lookup(result, 'powerState', 'keyName'),
        utils.lookup(result, 'powerState', 'name'),
    )])
    table.add_row(['active_transaction', formatting.active_txn(result)])
    table.add_row(['datacenter',
                   result['datacenter']['name'] or formatting.blank()])
    operating_system = utils.lookup(result,
                                    'operatingSystem',
                                    'softwareLicense',
                                    'softwareDescription') or {}
    table.add_row([
        'os',
        formatting.FormattedItem(
            operating_system.get('version') or formatting.blank(),
            operating_system.get('name') or formatting.blank()
        )])
    table.add_row(['os_version',
                   operating_system.get('version') or formatting.blank()])
    table.add_row(['cores', result['maxCpu']])
    table.add_row(['memory', formatting.mb_to_gb(result['maxMemory'])])
    table.add_row(['public_ip',
                   result['primaryIpAddress'] or formatting.blank()])
    table.add_row(['private_ip',
                   result['primaryBackendIpAddress'] or formatting.blank()])
    table.add_row(['private_only', result['privateNetworkOnlyFlag']])
    table.add_row(['private_cpu', result['dedicatedAccountHostOnlyFlag']])
    table.add_row(['created', result['createDate']])
    table.add_row(['modified', result['modifyDate']])
    if utils.lookup(result, 'billingItem') != []:
        table.add_row(['owner', formatting.FormattedItem(
            utils.lookup(result, 'billingItem', 'orderItem',
                         'order', 'userRecord',
                         'username') or formatting.blank(),
        )])
    else:
        table.add_row(['owner', formatting.blank()])

    vlan_table = formatting.Table(['type', 'number', 'id'])
    for vlan in result['networkVlans']:
        vlan_table.add_row([
            vlan['networkSpace'], vlan['vlanNumber'], vlan['id']])
    table.add_row(['vlans', vlan_table])

    if result.get('notes'):
        table.add_row(['notes', result['notes']])

    if price:
        table.add_row(['price rate',
                       result['billingItem']['recurringFee']])

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
