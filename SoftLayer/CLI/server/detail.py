"""Get details for a hardware device."""
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
@click.option('--price',
              is_flag=True,
              help='Show associated prices')
@environment.pass_env
def cli(env, identifier, passwords, price):
    """Get details for a hardware device."""

    hardware = SoftLayer.HardwareManager(env.client)

    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'

    hardware_id = helpers.resolve_id(hardware.resolve_ids,
                                     identifier,
                                     'hardware')
    result = hardware.get_hardware(hardware_id)
    result = utils.NestedDict(result)

    table.add_row(['id', result['id']])
    table.add_row(['guid', result['globalIdentifier'] or formatting.blank()])
    table.add_row(['hostname', result['hostname']])
    table.add_row(['domain', result['domain']])
    table.add_row(['fqdn', result['fullyQualifiedDomainName']])
    table.add_row(['status', result['hardwareStatus']['status']])
    table.add_row(['datacenter',
                   result['datacenter']['name'] or formatting.blank()])
    table.add_row(['cores', result['processorPhysicalCoreAmount']])
    table.add_row(['memory', formatting.gb(result['memoryCapacity'])])
    table.add_row(['public_ip',
                   result['primaryIpAddress'] or formatting.blank()])
    table.add_row(['private_ip',
                   result['primaryBackendIpAddress'] or formatting.blank()])
    table.add_row(['ipmi_ip',
                   result['networkManagementIpAddress'] or formatting.blank()])
    table.add_row([
        'os',
        formatting.FormattedItem(
            result['operatingSystem']['softwareLicense']
            ['softwareDescription']['referenceCode'] or formatting.blank(),
            result['operatingSystem']['softwareLicense']
            ['softwareDescription']['name'] or formatting.blank()
        )])

    table.add_row(
        ['created', result['provisionDate'] or formatting.blank()])

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
                       utils.lookup(result,
                                    'billingItem',
                                    'nextInvoiceTotalRecurringAmount')])

    if passwords:
        pass_table = formatting.Table(['username', 'password'])
        for item in result['operatingSystem']['passwords']:
            pass_table.add_row([item['username'], item['password']])
        table.add_row(['users', pass_table])

        pass_table = formatting.Table(['ipmi_username', 'password'])
        for item in result['remoteManagementAccounts']:
            pass_table.add_row([item['username'], item['password']])
        table.add_row(['remote users', pass_table])

    table.add_row(['tags', formatting.tags(result['tagReferences'])])

    # Test to see if this actually has a primary (public) ip address
    try:
        if not result['privateNetworkOnlyFlag']:
            ptr_domains = (env.client['Hardware_Server']
                           .getReverseDomainRecords(id=hardware_id))

            for ptr_domain in ptr_domains:
                for ptr in ptr_domain['resourceRecords']:
                    table.add_row(['ptr', ptr['data']])
    except SoftLayer.SoftLayerAPIError:
        pass

    env.fout(table)
