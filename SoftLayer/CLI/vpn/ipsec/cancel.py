"""Cancel a dedicated server."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@click.option('--immediate',
              is_flag=True,
              default=False,
              help="Cancels the server immediately (instead of on the billing anniversary)")
@click.option('--reason',
              help="An optional cancellation reason. See cancel-reasons for a list of available options")
@click.option('--comment',
              help="An optional comment to add to the cancellation ticket")
@environment.pass_env
def cli(env, identifier, immediate, reason, comment):
    """Cancel a IPSEC VPN tunnel context."""

    manager = SoftLayer.IPSECManager(env.client)
    context = manager.get_tunnel_context(identifier, mask='billingItem')

    result = manager.cancel_item(context['billingItem']['id'], immediate, reason, comment)

    if result:
        env.fout("Ipsec {} was cancelled.".format(identifier))
