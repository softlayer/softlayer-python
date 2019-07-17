"""Add an address translation to an IPSEC tunnel context."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
# from SoftLayer.CLI.exceptions import ArgumentError
# from SoftLayer.CLI.exceptions import CLIHalt


@click.command()
@click.argument('context_id', type=int)
@click.option('-s',
              '--static-ip',
              required=True,
              help='Static IP address value')
@click.option('-r',
              '--remote-ip',
              required=True,
              help='Remote IP address value')
@click.option('-n',
              '--note',
              default=None,
              help='Note value')
@environment.pass_env
def cli(env, context_id, static_ip, remote_ip, note):
    """Add an address translation to an IPSEC tunnel context.

    A separate configuration request should be made to realize changes on
    network devices.
    """
    manager = SoftLayer.IPSECManager(env.client)
    # ensure context can be retrieved by given id
    manager.get_tunnel_context(context_id)

    translation = manager.create_translation(context_id,
                                             static_ip=static_ip,
                                             remote_ip=remote_ip,
                                             notes=note)
    env.out('Created translation from {} to {} #{}'
            .format(static_ip, remote_ip, translation['id']))
