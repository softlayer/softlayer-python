"""List firewalls."""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import firewall
from SoftLayer.CLI import formatting

import click


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """List firewalls."""

    mgr = SoftLayer.FirewallManager(env.client)
    firewall_type, firewall_id = firewall.parse_id(identifier)

    if any([env.skip_confirmations,
            formatting.confirm("This action will cancel a firewall from your"
                               "account. Continue?")]):
        if firewall_type in ['vs', 'server']:
            mgr.cancel_firewall(firewall_id, dedicated=False)
        elif firewall_type == 'vlan':
            mgr.cancel_firewall(firewall_id, dedicated=True)
        return 'Firewall with id %s is being cancelled!' % identifier
    else:
        raise exceptions.CLIAbort('Aborted.')
