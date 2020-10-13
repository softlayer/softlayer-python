"""Get details of an Autoscale groups."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.autoscale import AutoScaleManager
from SoftLayer import utils


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Get details of an Autoscale groups."""

    autoscale = AutoScaleManager(env.client)
    group = autoscale.details(identifier)

    # Group Config Table
    table = formatting.KeyValueTable(["Group", "Value"])
    table.align['Group'] = 'l'
    table.align['Value'] = 'l'

    table.add_row(['Id', group.get('id')])
    # Ideally we would use regionalGroup->preferredDatacenter, but that generates an error.
    table.add_row(['Datacenter', group['regionalGroup']['locations'][0]['longName']])
    table.add_row(['Termination', utils.lookup(group, 'terminationPolicy', 'name')])
    table.add_row(['Minimum Members', group.get('minimumMemberCount')])
    table.add_row(['Maximum Members', group.get('maximumMemberCount')])
    table.add_row(['Current Members', group.get('virtualGuestMemberCount')])
    table.add_row(['Cooldown', "{} seconds".format(group.get('cooldown'))])
    table.add_row(['Last Action', utils.clean_time(group.get('lastActionDate'))])

    for network in group.get('networkVlans', []):
        network_type = utils.lookup(network, 'networkVlan', 'networkSpace')
        router = utils.lookup(network, 'networkVlan', 'primaryRouter', 'hostname')
        vlan_number = utils.lookup(network, 'networkVlan', 'vlanNumber')
        vlan_name = "{}.{}".format(router, vlan_number)
        table.add_row([network_type, vlan_name])

    env.fout(table)

    # Template Config Table
    config_table = formatting.KeyValueTable(["Template", "Value"])
    config_table.align['Template'] = 'l'
    config_table.align['Value'] = 'l'

    template = group.get('virtualGuestMemberTemplate')

    config_table.add_row(['Hostname', template.get('hostname')])
    config_table.add_row(['Domain', template.get('domain')])
    config_table.add_row(['Core', template.get('startCpus')])
    config_table.add_row(['Ram', template.get('maxMemory')])
    network = template.get('networkComponents')
    config_table.add_row(['Network', network[0]['maxSpeed'] if network else 'Default'])
    ssh_keys = template.get('sshKeys', [])
    ssh_manager = SoftLayer.SshKeyManager(env.client)
    for key in ssh_keys:
        # Label isn't included when retrieved from the AutoScale group...
        ssh_key = ssh_manager.get_key(key.get('id'))
        config_table.add_row(['SSH Key {}'.format(ssh_key.get('id')), ssh_key.get('label')])
    disks = template.get('blockDevices', [])
    disk_type = "Local" if template.get('localDiskFlag') else "SAN"

    for disk in disks:
        disk_image = disk.get('diskImage')
        config_table.add_row(['{} Disk {}'.format(disk_type, disk.get('device')), disk_image.get('capacity')])
    config_table.add_row(['OS', template.get('operatingSystemReferenceCode')])
    config_table.add_row(['Post Install', template.get('postInstallScriptUri') or 'None'])

    env.fout(config_table)

    # Policy Config Table
    policy_table = formatting.KeyValueTable(["Policy", "Cooldown"])
    policies = group.get('policies', [])
    for policy in policies:
        policy_table.add_row([policy.get('name'), policy.get('cooldown') or group.get('cooldown')])

    env.fout(policy_table)

    # Active Guests
    member_table = formatting.Table(['Id', 'Hostname', 'Created'], title="Active Guests")
    guests = group.get('virtualGuestMembers', [])
    for guest in guests:
        real_guest = guest.get('virtualGuest')
        member_table.add_row([
            real_guest.get('id'), real_guest.get('hostname'), utils.clean_time(real_guest.get('provisionDate'))
        ])
    env.fout(member_table)
