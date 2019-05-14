"""Edit hardware details."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier')
@click.option('--domain', '-D', help="Domain portion of the FQDN")
@click.option('--userfile', '-F', type=click.Path(exists=True, readable=True, resolve_path=True),
              help="Read userdata from file")
@click.option('--tag', '-g', multiple=True,
              help="Tags to set or empty string to remove all")
@click.option('--hostname', '-H', help="Host portion of the FQDN")
@click.option('--userdata', '-u', help="User defined metadata string")
@click.option('--public-speed', default=None, type=click.Choice(['0', '10', '100', '1000', '10000', '-1']),
              help="Public port speed. -1 is best speed available")
@click.option('--private-speed', default=None, type=click.Choice(['0', '10', '100', '1000', '10000', '-1']),
              help="Private port speed. -1 is best speed available")
@environment.pass_env
def cli(env, identifier, domain, userfile, tag, hostname, userdata, public_speed, private_speed):
    """Edit hardware details."""

    if userdata and userfile:
        raise exceptions.ArgumentError(
            '[-u | --userdata] not allowed with [-F | --userfile]')

    data = {
        'hostname': hostname,
        'domain': domain,
    }

    if userdata:
        data['userdata'] = userdata
    elif userfile:
        with open(userfile, 'r') as userfile_obj:
            data['userdata'] = userfile_obj.read()

    if tag:
        data['tags'] = ','.join(tag)

    mgr = SoftLayer.HardwareManager(env.client)
    hw_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'hardware')

    if not mgr.edit(hw_id, **data):
        raise exceptions.CLIAbort("Failed to update hardware")

    if public_speed is not None:
        mgr.change_port_speed(hw_id, True, int(public_speed))

    if private_speed is not None:
        mgr.change_port_speed(hw_id, False, int(private_speed))
