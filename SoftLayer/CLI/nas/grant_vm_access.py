import click
import json

import SoftLayer
from SoftLayer.CLI import environment

STORAGE_ENDPOINT = 'SoftLayer_Network_Storage'

@click.command()
@click.option('--vm-id', required=True)
@click.option('--storage-id', required=True)
@environment.pass_env
def cli(env, vm_id, storage_id):
    payload = {'id': vm_id}
    env.client[STORAGE_ENDPOINT].allowAccessFromVirtualGuest(
        payload, id=storage_id
    )
