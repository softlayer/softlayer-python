"""Lists status of all current and past registrations"""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils


@click.command()
@environment.pass_env
def cli(env):
    """Lists status of all current and past registrationst"""

    mgr = SoftLayer.NetworkManager(env.client)
    result = mgr.get_registrations()
    table = formatting.Table(['id', 'createDate', 'networkIdentifier',
                              'type', 'regionalInternet', 'status'])
    table.align['networkIdentifier'] = 'l'
    table.align['regionalInternet'] = 'l'
    table.align['status'] = 'l'
    for registration in result:
        table.add_row([registration['id'], utils.clean_time(registration['createDate']),
                       registration['networkIdentifier'],
                       registration['networkDetail']['detailType']['keyName'],
                       registration['regionalInternetRegistry']['keyName'],
                       registration['status']['keyName']])
    env.fout(table)
