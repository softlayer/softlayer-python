import click
import json

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import hardware

STORAGE_ENDPOINT = 'SoftLayer_Network_Storage'

@click.command()
@click.option('--order-id', required=False)
@click.option('--vm-id', required=False)
@click.option('--storage-id', required=True)
@environment.pass_env
def cli(env, order_id, vm_id, storage_id):
    if order_id and vm_id:
        raise ValueError('Should only specify order_id or vm_id but not both.')

    if order_id:
        hardware = SoftLayer.HardwareManager(env.client)
        hardware_ids = hardware.get_hardware_ids(order_id)
        for hardware_id in hardware_ids:
            payload = {'id': hardware_id}
            env.client[STORAGE_ENDPOINT].allowAccessFromHardware(
                payload, id=storage_id
            )

    if vm_id:
        payload = {'id': vm_id}
        env.client[STORAGE_ENDPOINT].allowAccessFromVirtualGuest(
            payload, id=storage_id
        )
