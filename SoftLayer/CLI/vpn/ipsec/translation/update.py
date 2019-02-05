"""Update an address translation for an IPSEC tunnel context."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI.exceptions import CLIHalt


@click.command()
@click.argument('context_id', type=int)
@click.option('-t',
              '--translation-id',
              required=True,
              type=int,
              help='Translation identifier to update')
@click.option('-s',
              '--static-ip',
              default=None,
              help='Static IP address value')
@click.option('-r',
              '--remote-ip',
              default=None,
              help='Remote IP address value')
@click.option('-n',
              '--note',
              default=None,
              help='Note value')
@environment.pass_env
def cli(env, context_id, translation_id, static_ip, remote_ip, note):
    """Update an address translation for an IPSEC tunnel context.

    A separate configuration request should be made to realize changes on
    network devices.
    """
    manager = SoftLayer.IPSECManager(env.client)
    succeeded = manager.update_translation(context_id,
                                           translation_id,
                                           static_ip=static_ip,
                                           remote_ip=remote_ip,
                                           notes=note)
    if succeeded:
        env.out('Updated translation #{}'.format(translation_id))
    else:
        raise CLIHalt('Failed to update translation #{}'.format(translation_id))
