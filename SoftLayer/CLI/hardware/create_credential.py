"""Create a password for a software component"""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@click.option('--username', '-U', required=True, help="The username part of the username/password pair")
@click.option('--password', '-P', required=True, help="The password part of the username/password pair.")
@click.option('--notes', '-n', help="A note string stored for this username/password pair.")
@click.option('--system', required=True, help="The name of this specific piece of software.")
@environment.pass_env
def cli(env, identifier, username, password, notes, system):
    """Create a password for a software component."""

    mgr = SoftLayer.HardwareManager(env.client)

    software = mgr.get_software_components(identifier)
    sw_id = ''
    try:
        for sw_instance in software:
            if (sw_instance['softwareLicense']['softwareDescription']['name']).lower() == system:
                sw_id = sw_instance['id']
    except KeyError as ex:
        raise exceptions.CLIAbort('System id not found') from ex

    template = {
        "notes": notes,
        "password": password,
        "softwareId": sw_id,
        "username": username,
        "software": {
            "hardwareId": identifier,
            "softwareLicense": {
                "softwareDescription": {
                    "name": system
                }
            }
        }}

    result = mgr.create_credential(template)

    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'
    table.add_row(['Software Id', result['id']])
    table.add_row(['Created', result['createDate']])
    table.add_row(['Username', result['username']])
    table.add_row(['Password', result['password']])
    table.add_row(['Notes', result['notes']])
    env.fout(table)
