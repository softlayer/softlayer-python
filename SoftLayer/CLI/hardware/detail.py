"""Get details for a hardware device."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer import utils

# pylint: disable=R0915


@click.command()
@click.argument('identifier')
@click.option('--passwords', is_flag=True, help='Show passwords (check over your shoulder!)')
@click.option('--price', is_flag=True, help='Show associated prices')
@click.option('--components', is_flag=True, default=False, help='Show associated hardware components')
@environment.pass_env
def cli(env, identifier, passwords, price, components):
    """Get details for a hardware device."""

    hardware = SoftLayer.HardwareManager(env.client)

    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'

    hardware_id = helpers.resolve_id(hardware.resolve_ids, identifier, 'hardware')
    result = hardware.get_hardware(hardware_id)
    result = utils.NestedDict(result)
    hard_drives = hardware.get_hard_drives(hardware_id)

    operating_system = utils.lookup(result, 'operatingSystem', 'softwareLicense', 'softwareDescription') or {}
    memory = formatting.gb(result.get('memoryCapacity', 0))
    owner = None
    if utils.lookup(result, 'billingItem') != []:
        owner = utils.lookup(result, 'billingItem', 'orderItem', 'order', 'userRecord', 'username')

    table_hard_drives = formatting.Table(['Name', 'Capacity', 'Serial #'])
    for drives in hard_drives:
        name = drives['hardwareComponentModel']['manufacturer'] + " " + drives['hardwareComponentModel']['name']
        capacity = str(drives['hardwareComponentModel']['hardwareGenericComponentModel']['capacity']) + " " + str(
            drives['hardwareComponentModel']['hardwareGenericComponentModel']['units'])
        serial = drives['serialNumber']

        table_hard_drives.add_row([name, capacity, serial])

    table.add_row(['id', result['id']])
    table.add_row(['guid', result['globalIdentifier'] or formatting.blank()])
    table.add_row(['hostname', result['hostname']])
    table.add_row(['domain', result['domain']])
    table.add_row(['fqdn', result['fullyQualifiedDomainName']])
    table.add_row(['status', result['hardwareStatus']['status']])
    table.add_row(['datacenter', result['datacenter']['name'] or formatting.blank()])
    table.add_row(['cores', result['processorPhysicalCoreAmount']])
    table.add_row(['memory', memory])
    table.add_row(['drives', table_hard_drives])
    table.add_row(['public_ip', result['primaryIpAddress'] or formatting.blank()])
    table.add_row(['private_ip', result['primaryBackendIpAddress'] or formatting.blank()])
    table.add_row(['ipmi_ip', result['networkManagementIpAddress'] or formatting.blank()])
    table.add_row(['os', operating_system.get('name') or formatting.blank()])
    table.add_row(['os_version', operating_system.get('version') or formatting.blank()])
    table.add_row(['created', result['provisionDate'] or formatting.blank()])
    table.add_row(['owner', owner or formatting.blank()])

    last_transaction = "{} ({})".format(utils.lookup(result, 'lastTransaction', 'transactionGroup', 'name'),
                                        utils.clean_time(utils.lookup(result, 'lastTransaction', 'modifyDate')))

    table.add_row(['last_transaction', last_transaction])
    table.add_row(['billing', 'Hourly' if result['hourlyBillingFlag'] else 'Monthly'])

    vlan_table = formatting.Table(['type', 'number', 'id'])
    for vlan in result['networkVlans']:
        vlan_table.add_row([vlan['networkSpace'], vlan['vlanNumber'], vlan['id']])

    table.add_row(['vlans', vlan_table])

    bandwidth = hardware.get_bandwidth_allocation(hardware_id)
    bw_table = _bw_table(bandwidth)
    table.add_row(['Bandwidth', bw_table])
    system_table = _system_table(result['activeComponents'])
    table.add_row(['System_data', system_table])

    if result.get('notes'):
        table.add_row(['notes', result['notes']])

    if price:
        total_price = utils.lookup(result, 'billingItem', 'nextInvoiceTotalRecurringAmount') or 0

        price_table = formatting.Table(['Item', 'CategoryCode', 'Recurring Price'])
        price_table.align['Item'] = 'l'

        price_table.add_row(['Total', '-', total_price])

        for item in utils.lookup(result, 'billingItem', 'nextInvoiceChildren') or []:
            price_table.add_row([item['description'], item['categoryCode'], item['nextInvoiceTotalRecurringAmount']])

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

    if components:
        components = hardware.get_components(identifier)
        components_table = formatting.Table(['name', 'Firmware version', 'Firmware build date', 'Type'])
        components_table.align['date'] = 'l'
        component_ids = []
        for hw_component in components:
            if hw_component['id'] not in component_ids:
                firmware = hw_component['hardwareComponentModel']['firmwares'][0]
                components_table.add_row([utils.lookup(hw_component, 'hardwareComponentModel', 'longDescription'),
                                          utils.lookup(firmware, 'version'),
                                          utils.clean_time(utils.lookup(firmware, 'createDate')),
                                          utils.lookup(hw_component, 'hardwareComponentModel',
                                                       'hardwareGenericComponentModel', 'hardwareComponentType',
                                                       'keyName')])
                component_ids.append(hw_component['id'])

        table.add_row(['components', components_table])

    table.add_row(['tags', formatting.tags(result['tagReferences'])])

    env.fout(table)


def _bw_table(bw_data):
    """Generates a bandwidth usage table"""
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


def _system_table(system_data):
    table = formatting.Table(['Type', 'name'])
    for system in system_data:
        table.add_row([utils.lookup(system, 'hardwareComponentModel',
                                    'hardwareGenericComponentModel',
                                    'hardwareComponentType', 'keyName'),
                       utils.lookup(system, 'hardwareComponentModel', 'longDescription')])
    return table
