"""Purge cached files from all edge nodes."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@click.argument('unique_id')
@click.argument('path')
@environment.pass_env
def cli(env, unique_id, path):
    """Creates a purge record and also initiates the purge call.

        Example:
             slcli cdn purge 9779455 /article/file.txt

        For more information see the following documentation: \n
        https://cloud.ibm.com/docs/infrastructure/CDN?topic=CDN-manage-your-cdn#purging-cached-content
    """

    manager = SoftLayer.CDNManager(env.client)
    result = manager.purge_content(unique_id, path)

    table = formatting.Table(['Date', 'Path', 'Saved', 'Status'])

    for data in result:
        table.add_row([
            data['date'],
            data['path'],
            data['saved'],
            data['status']
        ])

    env.fout(table)
