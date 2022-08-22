"""Cancel an IPSec service."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@click.option('--immediate',
              is_flag=True,
              default=False,
              help="Cancels the service  immediately (instead of on the billing anniversary)")
@click.option('--reason',
              help="An optional cancellation reason. See cancel-reasons for a list of available options")
@environment.pass_env
def cli(env, identifier, immediate, reason):
    """Cancel a IPSEC VPN tunnel context."""

    manager = SoftLayer.IPSECManager(env.client)
    context = manager.get_tunnel_context(identifier, mask='billingItem')

    if 'billingItem' not in context:
        raise SoftLayer.SoftLayerError("Cannot locate billing. May already be cancelled.")

    result = manager.cancel_item(context['billingItem']['id'], immediate, reason)

    if result:
        env.fout("Ipsec {} was cancelled.".format(identifier))
