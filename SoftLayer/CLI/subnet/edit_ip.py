"""Edit ip note"""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment


@click.command()
@click.argument('identifier')
@click.option('--note', help="set ip address note of subnet")
@environment.pass_env
def cli(env, identifier, note):
    """Set the note of the ipAddress"""

    data = {
        'note': note
    }
    mgr = SoftLayer.NetworkManager(env.client)
    ip_id = None
    if str.isdigit(identifier):
        ip_id = identifier
    else:
        ip_object = mgr.get_ip_by_address(identifier)
        ip_id = ip_object.get('id')
    mgr.set_subnet_ipddress_note(ip_id, data)
