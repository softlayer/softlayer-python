"""Cancel Network Vlan."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.managers.billing import BillingManager


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Cancel network vlan."""

    mgr = SoftLayer.NetworkManager(env.client)
    billing = BillingManager(env.client)
    if not (env.skip_confirmations or formatting.no_going_back(identifier)):
        raise exceptions.CLIAbort('Aborted')

    item = mgr.get_vlan(identifier).get('billingItem')
    if item:
        billing.cancel_item(item.get('id'), 'cancel by cli command')
        env.fout('Cancel Successfully')
    else:
        res = mgr.get_cancel_failure_reasons(identifier)
        raise exceptions.ArgumentError(res)
