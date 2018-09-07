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
@click.option('--limit', '-l',
              help='How many results to get in one api call, default is 100',
              default=100,
              show_default=True)
@environment.pass_env
def cli(env, sortby, limit):
    """List security groups."""

    mgr = SoftLayer.NetworkManager(env.client)

    table = formatting.Table(COLUMNS)
    table.sortby = sortby

    sgs = mgr.list_securitygroups(limit=limit)
    for secgroup in sgs:
        table.add_row([
            secgroup['id'],
            secgroup.get('name') or formatting.blank(),
            secgroup.get('description') or formatting.blank(),
        ])

    env.fout(table)
