import click
import json

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import hardware

STORAGE_ENDPOINT = 'SoftLayer_Network_Storage'

@click.command()
@click.option('--order-id', required=True)
@click.option('--storage-id', required=True)
@environment.pass_env
def cli(env, order_id, storage_id):
    hardware = SoftLayer.HardwareManager(env.client)

    hardware_ids = hardware.get_hardware_ids(order_id)
    for hardware_id in hardware_ids:
        payload = {'id': hardware_id}
        env.client[STORAGE_ENDPOINT].allowAccessFromHardware(
            payload, id=storage_id
        )
