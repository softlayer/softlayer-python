"""Check if a virtual server is ready."""
# :license: MIT, see LICENSE for more details.

import click
import json

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier')
@click.option('--wait', default=0, show_default=True, type=click.INT, help="Seconds to wait")
@click.option('--output-json', is_flag=True, default=False)
@environment.pass_env
def cli(env, identifier, wait, output_json=False):
    """Check if a virtual server is ready."""

    vsi = SoftLayer.VSManager(env.client)
    vs_id = helpers.resolve_id(vsi.resolve_ids, identifier, 'VS')
    ready = vsi.wait_for_ready(vs_id, wait)

    if output_json:
        env.fout(json.dumps({'ready': bool(ready)}))
        return

    if ready:
        env.fout("READY")
    else:
        raise exceptions.CLIAbort("Instance %s not ready" % vs_id)
