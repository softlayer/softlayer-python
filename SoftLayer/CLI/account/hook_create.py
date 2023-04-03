"""Order/create a provisioning script."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command(cls=SoftLayer.CLI.command.SLCommand)
@click.option('--name', '-N', required=True, prompt=True, help="The name of the hook.")
@click.option('--uri', '-U', required=True, prompt=True, help="The endpoint that the script will be downloaded")
@environment.pass_env
def cli(env, name, uri):
    """Order/create a provisioning script."""

    manager = SoftLayer.AccountManager(env.client)

    provisioning = manager.create_provisioning(name, uri)

    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'

    table.add_row(['Id', provisioning.get('id')])
    table.add_row(['Name', provisioning.get('name')])
    table.add_row(['Created', provisioning.get('createDate')])
    table.add_row(['Uri', provisioning.get('uri')])

    env.fout(table)
