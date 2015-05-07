"""Check if a virtual server is ready."""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import helpers

import click


@click.command()
@click.argument('identifier')
@click.option('--wait', default=0, type=click.INT, help="Name of the image")
@environment.pass_env
def cli(env, identifier, wait):
    """Check if a virtual server is ready."""

    vsi = SoftLayer.VSManager(env.client)
    vs_id = helpers.resolve_id(vsi.resolve_ids, identifier, 'VS')
    ready = vsi.wait_for_ready(vs_id, wait)
    if ready:
        return "READY"
    else:
        raise exceptions.CLIAbort("Instance %s not ready" % vs_id)
