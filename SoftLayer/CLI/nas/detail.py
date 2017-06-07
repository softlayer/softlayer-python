import click
import json

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils

NAS_PROPERTIES = 'id,username,serviceResourceBackendIpAddress,fileNetworkMountAddress'


@click.command()
@click.argument('nasid', type=int)
@environment.pass_env
def cli(env, nasid):
    account = env.client['Account']
    for nas in account.getNasNetworkStorage(mask=NAS_PROPERTIES):
        if int(nas['id']) == nasid:
            env.fout(json.dumps(nas))
            break
