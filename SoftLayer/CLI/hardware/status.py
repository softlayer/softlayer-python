import click
import json

import SoftLayer
from SoftLayer.CLI import environment


@click.command()
@click.argument('order_id', required=True)
@environment.pass_env
def cli(env, order_id):
    hardware = SoftLayer.HardwareManager(env.client)

    env.fout(json.dumps({
        'statuses': hardware.get_hardware_status_from_order(order_id)
    }))
