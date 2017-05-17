"""Updates an IPSEC tunnel context."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI.exceptions import CLIHalt


@click.command()
@click.argument('context_id', type=int)
@click.option('--friendly-name',
              default=None,
              help='Friendly name value')
# todo: Update to utilize custom IP address type
@click.option('--remote-peer',
              default=None,
              help='Remote peer IP address value')
@click.option('--preshared-key',
              default=None,
              help='Preshared key value')
@click.option('--p1-auth',
              '--phase1-auth',
              default=None,
              type=click.Choice(['MD5', 'SHA1', 'SHA256']),
              help='Phase 1 authentication value')
@click.option('--p1-crypto',
              '--phase1-crypto',
              default=None,
              type=click.Choice(['DES', '3DES', 'AES128', 'AES192', 'AES256']),
              help='Phase 1 encryption value')
@click.option('--p1-dh',
              '--phase1-dh',
              default=None,
              type=click.Choice(['0', '1', '2', '5']),
              help='Phase 1 diffie hellman group value')
@click.option('--p1-key-ttl',
              '--phase1-key-ttl',
              default=None,
              type=click.IntRange(120, 172800),
              help='Phase 1 key life value')
@click.option('--p2-auth',
              '--phase2-auth',
              default=None,
              type=click.Choice(['MD5', 'SHA1', 'SHA256']),
              help='Phase 2 authentication value')
@click.option('--p2-crypto',
              '--phase2-crypto',
              default=None,
              type=click.Choice(['DES', '3DES', 'AES128', 'AES192', 'AES256']),
              help='Phase 2 encryption value')
@click.option('--p2-dh',
              '--phase2-dh',
              default=None,
              type=click.Choice(['0', '1', '2', '5']),
              help='Phase 2 diffie hellman group value')
@click.option('--p2-forward-secrecy',
              '--phase2-forward-secrecy',
              default=None,
              type=click.IntRange(0, 1),
              help='Phase 2 perfect forward secrecy value')
@click.option('--p2-key-ttl',
              '--phase2-key-ttl',
              default=None,
              type=click.IntRange(120, 172800),
              help='Phase 2 key life value')
@environment.pass_env
def cli(env, context_id, friendly_name, remote_peer, preshared_key,
        phase1_auth, phase1_crypto, phase1_dh, phase1_key_ttl, phase2_auth,
        phase2_crypto, phase2_dh, phase2_forward_secrecy, phase2_key_ttl):
    """Update tunnel context properties.

    Updates are made atomically, so either all are accepted or none are.

    Key life values must be in the range 120-172800.

    Phase 2 perfect forward secrecy must be in the range 0-1.

    A separate configuration request should be made to realize changes on
    network devices.
    """
    manager = SoftLayer.IPSECManager(env.client)
    succeeded = manager.update_tunnel_context(
        context_id,
        friendly_name=friendly_name,
        remote_peer=remote_peer,
        preshared_key=preshared_key,
        phase1_auth=phase1_auth,
        phase1_crypto=phase1_crypto,
        phase1_dh=phase1_dh,
        phase1_key_ttl=phase1_key_ttl,
        phase2_auth=phase2_auth,
        phase2_crypto=phase2_crypto,
        phase2_dh=phase2_dh,
        phase2_forward_secrecy=phase2_forward_secrecy,
        phase2_key_ttl=phase2_key_ttl
    )
    if succeeded:
        env.out('Updated context #{}'.format(context_id))
    else:
        raise CLIHalt('Failed to update context #{}'.format(context_id))
