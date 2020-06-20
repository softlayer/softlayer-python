"""Edit ip note"""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment


@click.command()
@click.argument('identifier')
@click.option('--ip', required=True,
              help='Assume the ipAddress to set the note.')
@click.option('--note', help="set ip address note of subnet")
@environment.pass_env
def cli(env, identifier, ip, note):
    """Set the note of the ipAddress subnet"""

    data = {
        'note': note
    }
    mgr = SoftLayer.NetworkManager(env.client)
    ips = mgr.get_subnet(identifier, mask='id,ipAddresses[id,ipAddress]').get('ipAddresses')

    for address in ips:
        if ip == address.get('ipAddress'):
            mgr.set_subnet_ipddress_note(address.get('id'), data)
