"""Edit a virtual server's details."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import helpers


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
@click.option('--public-speed',
              help="Public port speed.",
              default=None,
              type=click.Choice(['0', '10', '100', '1000', '10000']))
@click.option('--private-speed',
              help="Private port speed.",
              default=None,
              type=click.Choice(['0', '10', '100', '1000', '10000']))
@environment.pass_env
def cli(env, identifier, domain, userfile, tag, hostname, userdata,
        public_speed, private_speed):
    """Edit a virtual server's details."""

    if userdata and userfile:
        raise exceptions.ArgumentError(
            '[-u | --userdata] not allowed with [-F | --userfile]')

    data = {}

    if userdata:
        data['userdata'] = userdata
    elif userfile:
        with open(userfile, 'r') as userfile_obj:
            data['userdata'] = userfile_obj.read()

    data['hostname'] = hostname
    data['domain'] = domain

    if tag:
        data['tags'] = ','.join(tag)

    vsi = SoftLayer.VSManager(env.client)
    vs_id = helpers.resolve_id(vsi.resolve_ids, identifier, 'VS')
    if not vsi.edit(vs_id, **data):
        raise exceptions.CLIAbort("Failed to update virtual server")

    if public_speed is not None:
        vsi.change_port_speed(vs_id, True, int(public_speed))

    if private_speed is not None:
        vsi.change_port_speed(vs_id, False, int(private_speed))
