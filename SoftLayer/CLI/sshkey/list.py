"""List SSH keys."""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting

import click


@click.command()
@click.option('--sortby',
              help='Column to sort by',
              type=click.Choice(['id',
                                 'label',
                                 'fingerprint',
                                 'notes']))
@environment.pass_env
def cli(env, sortby):
    """List SSH keys."""

    mgr = SoftLayer.SshKeyManager(env.client)
    keys = mgr.list_keys()

    table = formatting.Table(['id', 'label', 'fingerprint', 'notes'])
    table.sortby = sortby

    for key in keys:
        table.add_row([key['id'],
                       key.get('label'),
                       key.get('fingerprint'),
                       key.get('notes', '-')])

    return table
