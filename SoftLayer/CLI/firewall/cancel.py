"""Cancels a firewall."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@click.option('--firewall-type', required=True, show_default=True, default='vlan',
              type=click.Choice(['vlan', 'server'], case_sensitive=False),
              help='Firewall type.')
@environment.pass_env
def cli(env, identifier, firewall_type):
    """Cancels a firewall."""

    mgr = SoftLayer.FirewallManager(env.client)

    if not (env.skip_confirmations or
            formatting.confirm("This action will cancel a firewall from your account. Continue?")):
        raise exceptions.CLIAbort('Aborted.')

    if firewall_type == 'server':
        mgr.cancel_firewall(identifier, dedicated=False)
    else:
        mgr.cancel_firewall(identifier, dedicated=True)

    env.fout('Firewall with id %s is being cancelled!' % identifier)
