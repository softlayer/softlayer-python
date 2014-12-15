"""List SSL certificates."""
# :license: MIT, see LICENSE for more details.

import softlayer
from softlayer.cli import environment
from softlayer.cli import formatting

import click


@click.command()
@click.option('--status',
              default="all",
              type=click.Choice(['all', 'valid', 'expired']),
              help="Show certificates with this status")
@click.option('--sortby',
              type=click.Choice(['id',
                                 'common_name',
                                 'days_until_expire',
                                 'notes']),
              help="Column to sort by")
@environment.pass_env
def cli(env, status, sortby):
    """List SSL certificates."""
    manager = softlayer.SSLManager(env.client)

    certificates = manager.list_certs(status)

    table = formatting.Table(['id',
                              'common_name',
                              'days_until_expire',
                              'notes'])
    for certificate in certificates:
        table.add_row([
            certificate['id'],
            certificate['commonName'],
            certificate['validityDays'],
            certificate.get('notes', formatting.blank())
        ])
    table.sortby = sortby
    return table
