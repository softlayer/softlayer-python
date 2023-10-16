"""List VLANs this server can be attached to."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('hardware')
@environment.pass_env
def cli(env, hardware):
    """List VLANs this server can be attached to."""

    mgr = SoftLayer.HardwareManager(env.client)
    hw_id = helpers.resolve_id(mgr.resolve_ids, hardware, 'hardware')
    mask = (
        "mask[id,primaryIpAddress,"
        "networkVlansTrunkable[id,name,vlanNumber,fullyQualifiedName,networkSpace]]"
    )
    table = formatting.Table(["ID", "VLAN", "Name", "Space"])
    table.set_empty_message("No trunkable vlans found.")
    hw_components = env.client.call('SoftLayer_Hardware_Server', 'getNetworkComponents', id=hw_id, mask=mask)

    for component in hw_components:
        if component.get('primaryIpAddress'):
            for vlan in component.get('networkVlansTrunkable', []):
                table.add_row([
                    vlan.get('id'), vlan.get('fullyQualifiedName'), vlan.get('name'), vlan.get('networkSpace')
                ])

    env.fout(table)
