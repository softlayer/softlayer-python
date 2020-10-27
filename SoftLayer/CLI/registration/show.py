"""Display the RWhois information for your account."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils


@click.command()
@environment.pass_env
def cli(env):
    """Display the RWhois information for your account."""

    mgr = SoftLayer.NetworkManager(env.client)
    result = mgr.get_registrations()
    table = formatting.KeyValueTable(['id', 'createDate', 'networkIdentifier',
                                      'type', 'regionalInternet', 'status'])
    table.align['networkIdentifier'] = 'l'
    table.align['regionalInternet'] = 'l'
    for test in result:
        table.add_row([test['id'], utils.clean_time(test['createDate']),
                       test['networkIdentifier'],
                       test['networkDetail']['detailType']['keyName'],
                       test['regionalInternetRegistry']['keyName'],
                       test['status']['keyName']])
    env.fout(table)
