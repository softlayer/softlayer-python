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
@click.option('--software', required=True, help="The name of this specific piece of software.")
@environment.pass_env
def cli(env, identifier, username, password, notes, software):
    """Create a password for a software component."""

    mgr = SoftLayer.HardwareManager(env.client)

    software_components = mgr.get_software_components(identifier)
    software_id = ''
    try:
        for software_component in software_components:
            if software_component['softwareLicense']['softwareDescription']['name'].lower() == software.lower():
                software_id = software_component['id']
    except KeyError as ex:
        raise exceptions.CLIAbort('Software not found') from ex

    template = {
        "notes": notes,
        "password": password,
        "softwareId": software_id,
        "username": username
    }

    result = mgr.create_credential(template)

    table = formatting.KeyValueTable(['Name', 'Value'])
    table.align['Name'] = 'r'
    table.align['Value'] = 'l'
    table.add_row(['Software Credential Id', result['id']])
    table.add_row(['Created', result['createDate']])
    table.add_row(['Username', result['username']])
    table.add_row(['Password', result['password']])
    table.add_row(['Notes', result.get('notes') or formatting.blank()])
    env.fout(table)
