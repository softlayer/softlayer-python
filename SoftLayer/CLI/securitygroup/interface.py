"""Security group interface operations."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting

COLUMNS = ['networkComponentId',
           'virtualServerId',
           'hostname',
           'interface',
           'ipAddress', ]

REQUEST_COLUMNS = ['requestId']


@click.command()
@click.argument('securitygroup_id')
@click.option('--sortby',
              help='Column to sort by',
              type=click.Choice(COLUMNS))
@environment.pass_env
def interface_list(env, securitygroup_id, sortby):
    """List interfaces associated with security groups."""
    mgr = SoftLayer.NetworkManager(env.client)

    table = formatting.Table(COLUMNS)
    table.sortby = sortby

    mask = (
        '''networkComponentBindings[
            networkComponentId,
            networkComponent[
                id,
                port,
                guest[
                    id,
                    hostname,
                    primaryBackendIpAddress,
                    primaryIpAddress
                ]
            ]
        ]'''
    )

    secgroup = mgr.get_securitygroup(securitygroup_id, mask=mask)
    for binding in secgroup.get('networkComponentBindings', []):
        interface_id = binding['networkComponentId']
        try:
            interface = binding['networkComponent']
            vsi = interface['guest']
            vsi_id = vsi['id']
            hostname = vsi['hostname']
            priv_pub = 'PRIVATE' if interface['port'] == 0 else 'PUBLIC'
            ip_address = (vsi['primaryBackendIpAddress']
                          if interface['port'] == 0
                          else vsi['primaryIpAddress'])
        except KeyError:
            vsi_id = "N/A"
            hostname = "Not enough permission to view"
            priv_pub = "N/A"
            ip_address = "N/A"

        table.add_row([
            interface_id,
            vsi_id,
            hostname,
            priv_pub,
            ip_address
        ])

    env.fout(table)


@click.command()
@click.argument('securitygroup_id')
@click.option('--network-component', '-n',
              help=('The network component to associate '
                    'with the security group'))
@click.option('--server', '-s',
              help='The server ID to associate with the security group')
@click.option('--interface', '-i',
              help='The interface of the server to associate (public/private)')
@environment.pass_env
def add(env, securitygroup_id, network_component, server, interface):
    """Attach an interface to a security group."""
    _validate_args(network_component, server, interface)

    mgr = SoftLayer.NetworkManager(env.client)
    component_id = _get_component_id(env, network_component, server, interface)

    ret = mgr.attach_securitygroup_component(securitygroup_id,
                                             component_id)
    if not ret:
        raise exceptions.CLIAbort("Could not attach network component")

    table = formatting.Table(REQUEST_COLUMNS)
    table.add_row([ret['requestId']])

    env.fout(table)


@click.command()
@click.argument('securitygroup_id')
@click.option('--network-component', '-n',
              help=('The network component to remove from '
                    'with the security group'))
@click.option('--server', '-s',
              help='The server ID to remove from the security group')
@click.option('--interface', '-i',
              help='The interface of the server to remove (public/private)')
@environment.pass_env
def remove(env, securitygroup_id, network_component, server, interface):
    """Detach an interface from a security group."""
    _validate_args(network_component, server, interface)

    mgr = SoftLayer.NetworkManager(env.client)
    component_id = _get_component_id(env, network_component, server, interface)

    ret = mgr.detach_securitygroup_component(securitygroup_id,
                                             component_id)
    if not ret:
        raise exceptions.CLIAbort("Could not detach network component")

    table = formatting.Table(REQUEST_COLUMNS)
    table.add_row([ret['requestId']])

    env.fout(table)


def _validate_args(network_component, server, interface):
    use_server = bool(server and interface and not network_component)
    use_component = bool(network_component and not bool(server or interface))

    if not use_server and not use_component:
        raise exceptions.CLIAbort("Must set either --network-component "
                                  "or both --server and --interface")
    if use_server and interface.lower() not in ['public', 'private']:
        raise exceptions.CLIAbort(
            "Interface must be either 'public' or 'private'")


def _get_component_id(env, network_component, server, interface):
    use_server = bool(server and interface and not network_component)
    vs_mgr = SoftLayer.VSManager(env.client)

    if use_server:
        vs_mask = 'networkComponents[id, port]'
        vsi = vs_mgr.get_instance(server, mask=vs_mask)
        port = 0 if interface.lower() == 'private' else 1
        component = [c for c in vsi['networkComponents'] if c['port'] == port]
        if len(component) != 1:
            raise exceptions.CLIAbort("Instance %s has no %s interface"
                                      % (server, interface))
        component_id = component[0]['id']
    else:
        component_id = network_component

    return component_id
