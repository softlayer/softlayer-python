"""Create new firewall."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting


@click.command()
@click.argument('target')
@click.option('--firewall-type',
              type=click.Choice(['vs', 'vlan', 'server']),
              help='Firewall type',
              required=True)
@click.option('-ha', '--high-availability',
              is_flag=True,
              help='High available firewall option')
@environment.pass_env
def cli(env, target, firewall_type, high_availability):
    """Create new firewall.

    TARGET: Id of the server the firewall will protect
    """

    mgr = SoftLayer.FirewallManager(env.client)

    if not env.skip_confirmations:
        if firewall_type == 'vlan':
            pkg = mgr.get_dedicated_package(ha_enabled=high_availability)
        elif firewall_type == 'vs':
            pkg = mgr.get_standard_package(target, is_virt=True)
        elif firewall_type == 'server':
            pkg = mgr.get_standard_package(target, is_virt=False)

        if not pkg:
            exceptions.CLIAbort(
                "Unable to add firewall - Is network public enabled?")

        env.out("******************")
        env.out("Product: %s" % pkg[0]['description'])
        env.out("Price: $%s monthly" % pkg[0]['prices'][0]['recurringFee'])
        env.out("******************")

        if not formatting.confirm("This action will incur charges on your "
                                  "account. Continue?"):
            raise exceptions.CLIAbort('Aborted.')

    if firewall_type == 'vlan':
        mgr.add_vlan_firewall(target, ha_enabled=high_availability)
    elif firewall_type == 'vs':
        mgr.add_standard_firewall(target, is_virt=True)
    elif firewall_type == 'server':
        mgr.add_standard_firewall(target, is_virt=False)

    env.fout("Firewall is being created!")
