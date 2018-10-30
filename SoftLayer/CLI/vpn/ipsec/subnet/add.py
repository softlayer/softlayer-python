"""Add a subnet to an IPSEC tunnel context."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI.custom_types import NetworkParamType
from SoftLayer.CLI import environment
from SoftLayer.CLI.exceptions import ArgumentError
from SoftLayer.CLI.exceptions import CLIHalt


@click.command()
@click.argument('context_id', type=int)
@click.option('-s',
              '--subnet-id',
              default=None,
              type=int,
              help='Subnet identifier to add')
@click.option('-t',
              '--subnet-type',
              '--type',
              required=True,
              type=click.Choice(['internal', 'remote', 'service']),
              help='Subnet type to add')
@click.option('-n',
              '--network-identifier',
              '--network',
              default=None,
              type=NetworkParamType(),
              help='Subnet network identifier to create')
@environment.pass_env
def cli(env, context_id, subnet_id, subnet_type, network_identifier):
    """Add a subnet to an IPSEC tunnel context.

    A subnet id may be specified to link to the existing tunnel context.

    Otherwise, a network identifier in CIDR notation should be specified,
    indicating that a subnet resource should first be created before associating
    it with the tunnel context. Note that this is only supported for remote
    subnets, which are also deleted upon failure to attach to a context.

    A separate configuration request should be made to realize changes on
    network devices.
    """
    create_remote = False
    if subnet_id is None:
        if network_identifier is None:
            raise ArgumentError('Either a network identifier or subnet id '
                                'must be provided.')
        if subnet_type != 'remote':
            raise ArgumentError('Unable to create {} subnets'
                                .format(subnet_type))
        create_remote = True

    manager = SoftLayer.IPSECManager(env.client)
    context = manager.get_tunnel_context(context_id)

    if create_remote:
        subnet = manager.create_remote_subnet(context['accountId'],
                                              identifier=network_identifier[0],
                                              cidr=network_identifier[1])
        subnet_id = subnet['id']
        env.out('Created subnet {}/{} #{}'
                .format(network_identifier[0],
                        network_identifier[1],
                        subnet_id))

    succeeded = False
    if subnet_type == 'internal':
        succeeded = manager.add_internal_subnet(context_id, subnet_id)
    elif subnet_type == 'remote':
        succeeded = manager.add_remote_subnet(context_id, subnet_id)
    elif subnet_type == 'service':
        succeeded = manager.add_service_subnet(context_id, subnet_id)

    if succeeded:
        env.out('Added {} subnet #{}'.format(subnet_type, subnet_id))
    else:
        raise CLIHalt('Failed to add {} subnet #{}'
                      .format(subnet_type, subnet_id))
