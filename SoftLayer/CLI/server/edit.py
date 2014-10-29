"""Edit hardware details."""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import helpers

import click


@click.command()
@click.argument('identifier')
@click.option('--domain', '-D', help="Domain portion of the FQDN")
@click.option('--userfile', '-F',
              help="Read userdata from file",
              type=click.Path(exists=True, readable=True, resolve_path=True))
@click.option('--hostname', '-H', help="Host portion of the FQDN")
@click.option('--userdata', '-u', help="User defined metadata string")
@environment.pass_env
def cli(env, identifier, domain, userfile, hostname, userdata):
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

    mgr = SoftLayer.HardwareManager(env.client)
    hw_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'hardware')

    if not mgr.edit(hw_id, **data):
        raise exceptions.CLIAbort("Failed to update hardware")
