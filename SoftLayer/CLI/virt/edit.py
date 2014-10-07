"""Edit a virtual server's details."""
# :license: MIT, see LICENSE for more details.

import os
import os.path

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import helpers

import click


@click.command()
@click.argument('identifier')
@click.option('--domain', '-D', help="Domain portion of the FQDN")
@click.option('--userfile', '-F', help="Read userdata from file")
@click.option('--tag', '-g',
              help="Comma list of tags to set or empty string to remove all")
@click.option('--hostname', '-H',
              help="Host portion of the FQDN. example: server")
@click.option('--userdata', '-u', help="User defined metadata string")
@environment.pass_env
def cli(env, identifier, domain, userfile, tag, hostname, userdata):
    """Edit a virtual server's details."""

    data = {}

    if userdata and userfile:
        raise exceptions.ArgumentError(
            '[-u | --userdata] not allowed with [-F | --userfile]')
    if userfile:
        if not os.path.exists(userfile):
            raise exceptions.ArgumentError(
                'File does not exist [-u | --userfile] = %s' % userfile)

    if userdata:
        data['userdata'] = userdata
    elif userfile:
        with open(userfile, 'r') as userfile_obj:
            data['userdata'] = userfile_obj.read()

    data['hostname'] = hostname
    data['domain'] = domain
    data['tag'] = tag

    vsi = SoftLayer.VSManager(env.client)
    vs_id = helpers.resolve_id(vsi.resolve_ids, identifier, 'VS')
    if not vsi.edit(vs_id, **data):
        raise exceptions.CLIAbort("Failed to update virtual server")
