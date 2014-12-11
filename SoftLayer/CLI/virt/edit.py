"""Edit a virtual server's details."""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import helpers

import click


@click.command()
@click.argument('identifier')
@click.option('--domain', '-D', help="Domain portion of the FQDN")
@click.option('--hostname', '-H',
              help="Host portion of the FQDN. example: server")
@click.option('--tag', '-g',
              multiple=True,
              help="Tags to set or empty string to remove all")
@click.option('--userdata', '-u', help="User defined metadata string")
@click.option('--userfile', '-F',
              help="Read userdata from file",
              type=click.Path(exists=True, readable=True, resolve_path=True))
@environment.pass_env
def cli(env, identifier, domain, userfile, tag, hostname, userdata):
    """Edit a virtual server's details."""

    data = {}

    if userdata and userfile:
        raise exceptions.ArgumentError(
            '[-u | --userdata] not allowed with [-F | --userfile]')

    if userdata:
        data['userdata'] = userdata
    elif userfile:
        with open(userfile, 'r') as userfile_obj:
            data['userdata'] = userfile_obj.read()

    data['hostname'] = hostname
    data['domain'] = domain
    data['tags'] = ','.join(tag)

    vsi = SoftLayer.VSManager(env.client)
    vs_id = helpers.resolve_id(vsi.resolve_ids, identifier, 'VS')
    if not vsi.edit(vs_id, **data):
        raise exceptions.CLIAbort("Failed to update virtual server")
