"""Trunk a VLAN to this server."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import helpers


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('hardware', nargs=1)
@click.argument('vlans', nargs=-1)
@environment.pass_env
def cli(env, hardware, vlans):
    """Trunk a VLAN to this server.

    HARDWARE is the id of the server
    VLANS is the ID, name, or number of the VLANs you want to add. Multiple vlans can be added at the same time.
    It is recommended to use the vlan ID, especially if you have multiple vlans with the same name/number.
    """

    if not vlans:
        raise exceptions.ArgumentError("Error: Missing argument 'VLANS'.")
    h_mgr = SoftLayer.HardwareManager(env.client)
    n_mgr = SoftLayer.NetworkManager(env.client)
    hw_id = helpers.resolve_id(h_mgr.resolve_ids, hardware, 'hardware')
    # Enclosing in quotes is required for any input that has a space in it.
    # "Public DAL10" for example needs to be sent to search as \"Public DAL10\"
    sl_vlans = n_mgr.search_for_vlan(" ".join(f"\"{v}\"" for v in vlans))
    if not sl_vlans:
        raise exceptions.ArgumentError(f"No vlans found matching {' '.join(vlans)}")
    add_vlans = parse_vlans(sl_vlans)
    component_mask = "mask[id, name, port, macAddress, primaryIpAddress]"
    # NEXT: Add nice output / exception handling
    if len(add_vlans['public']) > 0:
        components = h_mgr.get_network_components(hw_id, mask=component_mask, space='public')
        for c in components:
            if c.get('primaryIpAddress'):
                h_mgr.trunk_vlan(c.get('id'), add_vlans['public'])
    if len(add_vlans['private']) > 0:
        components = h_mgr.get_network_components(hw_id, mask=component_mask, space='private')
        for c in components:
            if c.get('primaryIpAddress'):
                h_mgr.trunk_vlan(c.get('id'), add_vlans['private'])


def parse_vlans(vlans):
    """returns a dictionary mapping for public / private vlans"""

    pub_vlan = []
    pri_vlan = []
    for vlan in vlans:
        print(f"{vlan.get('networkSpace')} | {vlan.get('id')} -> {vlan.get('vlanNumber')}")
        if vlan.get('networkSpace') == "PUBLIC":
            pub_vlan.append(vlan)
        else:
            pri_vlan.append(vlan)
    return {"public": pub_vlan, "private": pri_vlan}
