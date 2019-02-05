"""Check if a server is ready."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier')
@click.option('--wait', default=0, show_default=True, type=click.INT,
              help="Seconds to wait")
@environment.pass_env
def cli(env, identifier, wait):
    """Check if a server is ready."""

    compute = SoftLayer.HardwareManager(env.client)
    compute_id = helpers.resolve_id(compute.resolve_ids, identifier,
                                    'hardware')
    ready = compute.wait_for_ready(compute_id, wait)
    if ready:
        env.fout("READY")
    else:
        raise exceptions.CLIAbort("Server %s not ready" % compute_id)
