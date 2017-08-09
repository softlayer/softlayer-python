"""List securitygroups."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting

COLUMNS = ['id',
           'name',
           'description', ]


@click.command()
@click.option('--sortby',
              help='Column to sort by',
              type=click.Choice(COLUMNS))
@environment.pass_env
def cli(env, sortby):
    """List security groups."""

    mgr = SoftLayer.NetworkManager(env.client)

    table = formatting.Table(COLUMNS)
    table.sortby = sortby

    sgs = mgr.list_securitygroups()
    for secgroup in sgs:
        table.add_row([
            secgroup['id'],
            secgroup.get('name') or formatting.blank(),
            secgroup.get('description') or formatting.blank(),
        ])

    env.fout(table)
