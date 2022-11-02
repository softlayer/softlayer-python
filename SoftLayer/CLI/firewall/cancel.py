"""Cancels a firewall."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import firewall
from SoftLayer.CLI import formatting


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Cancels a firewall.

        E.g.

           slcli firewall cancel multiVlan:123456

    """

    mgr = SoftLayer.FirewallManager(env.client)
    firewall_type, firewall_id = firewall.parse_id(identifier)

    if not (env.skip_confirmations or
            formatting.confirm("This action will cancel a firewall from your "
                               "account. Continue?")):
        raise exceptions.CLIAbort('Aborted.')

    if firewall_type in ['vs', 'server']:
        mgr.cancel_firewall(firewall_id, dedicated=False)
    elif firewall_type == 'vlan':
        mgr.cancel_firewall(firewall_id, dedicated=True)
    else:
        raise exceptions.CLIAbort('Unknown firewall type: %s' % firewall_type)

    env.fout('Firewall with id %s is being cancelled!' % identifier)
