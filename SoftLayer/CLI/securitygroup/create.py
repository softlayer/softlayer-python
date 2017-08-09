"""Create security groups."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@click.option('--name', '-n',
              help="The name of the security group")
@click.option('--description', '-d',
              help="The description of the security group")
@environment.pass_env
def cli(env, name, description):
    """Create a security group."""
    mgr = SoftLayer.NetworkManager(env.client)

    result = mgr.create_securitygroup(name, description)
    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'
    table.add_row(['id', result['id']])
    table.add_row(['name',
                   result.get('name') or formatting.blank()])
    table.add_row(['description',
                   result.get('description') or formatting.blank()])
    table.add_row(['created', result['createDate']])

    env.fout(table)
