"""Cancel Network Vlan."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Cancel network VLAN."""

    mgr = SoftLayer.NetworkManager(env.client)

    if not (env.skip_confirmations or formatting.no_going_back(identifier)):
        raise exceptions.CLIAbort('Aborted')

    reasons = mgr.get_cancel_failure_reasons(identifier)
    if len(reasons) > 0:
        raise exceptions.CLIAbort(reasons)
    item = mgr.get_vlan(identifier).get('billingItem')
    if item:
        mgr.cancel_item(item.get('id'),
                        True,
                        'Cancel by cli command',
                        'Cancel by cli command')
    else:
        raise exceptions.CLIAbort(
            "VLAN is an automatically assigned and free of charge VLAN,"
            " it will automatically be removed from your account when it is empty")
