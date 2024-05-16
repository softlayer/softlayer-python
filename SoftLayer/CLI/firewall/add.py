"""Add a server to the firewall"""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('target')
@click.option('--firewall-type', type=click.Choice(['vs', 'vlan', 'server']), help='Firewall type', required=True)
@click.option("-h", '--high-availability', is_flag=True, help='High available firewall option')
@click.option('-f', '--force',  default=False, is_flag=True, help="Force addition of firewall to the server")
@environment.pass_env
def cli(env, target, firewall_type, high_availability, force):
    """Create new firewall.

    TARGET: Id of the server the firewall will protect
    """

    mgr = SoftLayer.FirewallManager(env.client)
    pkg = {}
    if not env.skip_confirmations:
        if firewall_type == 'vlan':
            pkg = mgr.get_dedicated_package(ha_enabled=high_availability)
        elif firewall_type == 'vs':
            pkg = mgr.get_standard_package(target, is_virt=True)
        elif firewall_type == 'server':
            pkg = mgr.get_standard_package(target, is_virt=False)

        if not pkg:
            exceptions.CLIAbort("Unable to add firewall - Is network public enabled?")

        click.echo("******************")
        click.echo("Product: %s" % pkg[0]['description'])
        click.echo("Price: $%s monthly" % pkg[0]['prices'][0]['recurringFee'])
        click.echo("******************")

        if not force:
            if not formatting.confirm("This action will incur charges on your account. Continue?"):
                raise exceptions.CLIAbort('Aborted.')

    if firewall_type == 'vlan':
        mgr.add_vlan_firewall(target, ha_enabled=high_availability)
    elif firewall_type == 'vs':
        mgr.add_standard_firewall(target, is_virt=True)
    elif firewall_type == 'server':
        mgr.add_standard_firewall(target, is_virt=False)

    click.echo("Firewall is being created!")
