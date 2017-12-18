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
@click.option('--passwords', is_flag=True, help='Show passwords (check over your shoulder!)')
@click.option('--price', is_flag=True, help='Show associated prices')
@environment.pass_env
def cli(env, identifier, passwords, price):
    """Get details for a hardware device."""

    hardware = SoftLayer.HardwareManager(env.client)

    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'

    hardware_id = helpers.resolve_id(hardware.resolve_ids, identifier, 'hardware')
    result = hardware.get_hardware(hardware_id)
    result = utils.NestedDict(result)

    operating_system = utils.lookup(result, 'operatingSystem', 'softwareLicense', 'softwareDescription') or {}
    memory = formatting.gb(result.get('memoryCapacity', 0))
    owner = None
    if utils.lookup(result, 'billingItem') != []:
        owner = utils.lookup(result, 'billingItem', 'orderItem', 'order', 'userRecord', 'username')

    table.add_row(['id', result['id']])
    table.add_row(['guid', result['globalIdentifier'] or formatting.blank()])
    table.add_row(['hostname', result['hostname']])
    table.add_row(['domain', result['domain']])
    table.add_row(['fqdn', result['fullyQualifiedDomainName']])
    table.add_row(['status', result['hardwareStatus']['status']])
    table.add_row(['datacenter', result['datacenter']['name'] or formatting.blank()])
    table.add_row(['cores', result['processorPhysicalCoreAmount']])
    table.add_row(['memory', memory])
    table.add_row(['public_ip', result['primaryIpAddress'] or formatting.blank()])
    table.add_row(['private_ip', result['primaryBackendIpAddress'] or formatting.blank()])
    table.add_row(['ipmi_ip', result['networkManagementIpAddress'] or formatting.blank()])
    table.add_row(['os', operating_system.get('name') or formatting.blank()])
    table.add_row(['os_version', operating_system.get('version') or formatting.blank()])
    table.add_row(['created', result['provisionDate'] or formatting.blank()])
    table.add_row(['owner', owner or formatting.blank()])

    vlan_table = formatting.Table(['type', 'number', 'id'])
    for vlan in result['networkVlans']:
        vlan_table.add_row([vlan['networkSpace'], vlan['vlanNumber'], vlan['id']])

    table.add_row(['vlans', vlan_table])

    if result.get('notes'):
        table.add_row(['notes', result['notes']])

    if price:
        total_price = utils.lookup(result, 'billingItem', 'nextInvoiceTotalRecurringAmount') or 0

        price_table = formatting.Table(['Item', 'Recurring Price'])
        price_table.add_row(['Total', total_price])

        for item in utils.lookup(result, 'billingItem', 'children') or []:
            price_table.add_row([item['description'], item['nextInvoiceTotalRecurringAmount']])

        table.add_row(['prices', price_table])

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

    env.fout(table)
