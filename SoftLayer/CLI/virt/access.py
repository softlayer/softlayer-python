"""Get user access details a virtual server."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Get user access details a virtual server."""

    vsi = SoftLayer.VSManager(env.client)
    access_logs = vsi.browser_access_log(identifier)

    table = formatting.KeyValueTable(['Username', 'Source IP', 'Port', 'Date', 'Event', 'Message'])
    for log in access_logs:
        table.add_row([log.get('username'), log.get('sourceIp'), log.get('sourcePort'), log.get('createDate'),
                       log.get('eventType'), log.get('message')])

    env.fout(table)
