"""Purge cached files from all edge nodes."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@click.argument('account_id')
@click.argument('content_url', nargs=-1)
@environment.pass_env
def cli(env, account_id, content_url):
    """Purge cached files from all edge nodes.

    Examples:
         slcli cdn purge 97794 http://example.com/cdn/file.txt
         slcli cdn purge 97794 http://example.com/cdn/file.txt https://dal01.example.softlayer.net/image.png
    """

    manager = SoftLayer.CDNManager(env.client)
    content_list = manager.purge_content(account_id, content_url)

    table = formatting.Table(['url', 'status'])

    for content in content_list:
        table.add_row([
            content['url'],
            content['statusCode']
        ])

    env.fout(table)
