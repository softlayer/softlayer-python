"""Manage LBaaS Pools/Listeners."""
import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import helpers
from SoftLayer.exceptions import SoftLayerAPIError


# pylint: disable=unused-argument
def sticky_option(ctx, param, value):
    """parses sticky cli option"""
    if value:
        return 'SOURCE_IP'
    return None


def parse_server(ctx, param, values):
    """Splits out the IP, Port, Weight from the --server argument for l7pools"""
    servers = []
    for server in values:
        splitout = server.split(':')
        if len(splitout) != 3:
            raise exceptions.ArgumentError(
                "--server needs a port and a weight. {} improperly formatted".format(server))
        server = {
            'address': splitout[0],
            'port': splitout[1],
            'weight': splitout[2]
        }
        servers.append(server)

    return servers


@click.command()
@click.argument('identifier')
@click.option('--frontProtocol', '-P', default='HTTP', type=click.Choice(['HTTP', 'HTTPS', 'TCP']), show_default=True,
              help="Protocol type to use for incoming connections")
@click.option('--backProtocol', '-p', type=click.Choice(['HTTP', 'HTTPS', 'TCP']),
              help="Protocol type to use when connecting to backend servers. Defaults to whatever --frontProtocol is.")
@click.option('--frontPort', '-f', required=True, type=int, help="Internet side port")
@click.option('--backPort', '-b', required=True, type=int, help="Private side port")
@click.option('--method', '-m', default='ROUNDROBIN', show_default=True, help="Balancing Method",
              type=click.Choice(['ROUNDROBIN', 'LEASTCONNECTION', 'WEIGHTED_RR']))
@click.option('--connections', '-c', type=int, help="Maximum number of connections to allow.")
@click.option('--sticky', '-s', is_flag=True, callback=sticky_option, help="Make sessions sticky based on source_ip.")
@click.option('--sslCert', '-x', help="SSL certificate ID. See `slcli ssl list`")
@environment.pass_env
def add(env, identifier, **args):
    """Adds a listener to the identifier LB"""

    mgr = SoftLayer.LoadBalancerManager(env.client)
    uuid, _ = mgr.get_lbaas_uuid_id(identifier)

    new_listener = {
        'backendPort': args.get('backport'),
        'backendProtocol': args.get('backprotocol') if args.get('backprotocol') else args.get('frontprotocol'),
        'frontendPort': args.get('frontport'),
        'frontendProtocol': args.get('frontprotocol'),
        'loadBalancingMethod': args.get('method'),
        'maxConn': args.get('connections', None),
        'sessionType': args.get('sticky'),
        'tlsCertificateId': args.get('sslcert')
    }

    try:
        mgr.add_lb_listener(uuid, new_listener)
        click.secho("Success", fg='green')
    except SoftLayerAPIError as exception:
        click.secho("ERROR: {}".format(exception.faultString), fg='red')


@click.command()
@click.argument('identifier')
@click.argument('listener')
@click.option('--frontProtocol', '-P', type=click.Choice(['HTTP', 'HTTPS', 'TCP']),
              help="Protocol type to use for incoming connections")
@click.option('--backProtocol', '-p', type=click.Choice(['HTTP', 'HTTPS', 'TCP']),
              help="Protocol type to use when connecting to backend servers. Defaults to whatever --frontProtocol is.")
@click.option('--frontPort', '-f', type=int, help="Internet side port")
@click.option('--backPort', '-b', type=int, help="Private side port")
@click.option('--method', '-m', help="Balancing Method",
              type=click.Choice(['ROUNDROBIN', 'LEASTCONNECTION', 'WEIGHTED_RR']))
@click.option('--connections', '-c', type=int, help="Maximum number of connections to allow.")
@click.option('--clientTimeout', '-t', type=int,
              help="maximum idle time in seconds(Range: 1 to 7200).")
@click.option('--sticky', '-s', is_flag=True, callback=sticky_option, help="Make sessions sticky based on source_ip.")
@click.option('--sslCert', '-x', help="SSL certificate ID. See `slcli ssl list`")
@environment.pass_env
def edit(env, identifier, listener, **args):
    """Updates a listener's configuration.

    LISTENER should be a UUID, and can be found from `slcli lb detail <IDENTIFIER>`
    """

    mgr = SoftLayer.LoadBalancerManager(env.client)
    uuid, _ = mgr.get_lbaas_uuid_id(identifier)

    new_listener = {
        'listenerUuid': listener
    }

    arg_to_option = {
        'frontprotocol': 'frontendProtocol',
        'backprotocol': 'backendProtocol',
        'frontport': 'frontendPort',
        'backport': 'backendPort',
        'method': 'loadBalancingMethod',
        'connections': 'maxConn',
        'sticky': 'sessionType',
        'clienttimeout': 'clientTimeout',
        'sslcert': 'tlsCertificateId'
    }

    for key, value in args.items():
        if value:
            new_listener[arg_to_option[key]] = value

    try:
        mgr.add_lb_listener(uuid, new_listener)
        click.secho("Success", fg='green')
    except SoftLayerAPIError as exception:
        click.secho("ERROR: {}".format(exception.faultString), fg='red')


@click.command()
@click.argument('identifier')
@click.argument('listener')
@environment.pass_env
def delete(env, identifier, listener):
    """Removes the listener from identified LBaaS instance

    LISTENER should be a UUID, and can be found from `slcli lb detail <IDENTIFIER>`
    """

    mgr = SoftLayer.LoadBalancerManager(env.client)
    uuid, _ = mgr.get_lbaas_uuid_id(identifier)
    try:
        mgr.remove_lb_listener(uuid, listener)
        click.secho("Success", fg='green')
    except SoftLayerAPIError as exception:
        click.secho("ERROR: {}".format(exception.faultString), fg='red')


@click.command()
@click.argument('identifier')
# https://sldn.softlayer.com/reference/datatypes/SoftLayer_Network_LBaaS_L7Pool/
@click.option('--name', '-n', required=True, help="Name for this L7 pool.")
@click.option('--method', '-m', help="Balancing Method.", default='ROUNDROBIN', show_default=True,
              type=click.Choice(['ROUNDROBIN', 'LEASTCONNECTION', 'WEIGHTED_RR']))
@click.option('--protocol', '-P', type=click.Choice(['HTTP', 'HTTPS']), default='HTTP',
              show_default=True, help="Protocol type to use for incoming connections")
# https://sldn.softlayer.com/reference/datatypes/SoftLayer_Network_LBaaS_L7Member/
@helpers.multi_option('--server', '-S', callback=parse_server, required=True,
                      help="Backend servers that are part of this pool. Format is colon deliminated. "
                           "BACKEND_IP:PORT:WEIGHT. eg. 10.0.0.1:80:50")
# https://sldn.softlayer.com/reference/datatypes/SoftLayer_Network_LBaaS_L7HealthMonitor/
@click.option('--healthPath', default='/', show_default=True, help="Health check path.")
@click.option('--healthInterval', default=5, type=int, show_default=True, help="Health check interval between checks.")
@click.option('--healthRetry', default=2, type=int, show_default=True,
              help="Health check number of times before marking as DOWN.")
@click.option('--healthTimeout', default=2, type=int, show_default=True, help="Health check timeout.")
# https://sldn.softlayer.com/reference/datatypes/SoftLayer_Network_LBaaS_L7SessionAffinity/
@click.option('--sticky', '-s', is_flag=True, callback=sticky_option, help="Make sessions sticky based on source_ip.")
@environment.pass_env
def l7pool_add(env, identifier, **args):
    """Adds a new l7 pool

    -S is in colon deliminated format to make grouping IP:port:weight a bit easier.
    """

    mgr = SoftLayer.LoadBalancerManager(env.client)
    uuid, _ = mgr.get_lbaas_uuid_id(identifier)

    pool_main = {
        'name': args.get('name'),
        'loadBalancingAlgorithm': args.get('method'),
        'protocol': args.get('protocol')
    }

    pool_members = list(args.get('server'))

    pool_health = {
        'interval': args.get('healthinterval'),
        'timeout': args.get('healthtimeout'),
        'maxRetries': args.get('healthretry'),
        'urlPath': args.get('healthpath')
    }

    pool_sticky = {
        'type': args.get('sticky')
    }

    try:
        mgr.add_lb_l7_pool(uuid, pool_main, pool_members, pool_health, pool_sticky)
        click.secho("Success", fg='green')
    except SoftLayerAPIError as exception:
        click.secho("ERROR: {}".format(exception.faultString), fg='red')


@click.command()
@click.argument('identifier')
@environment.pass_env
def l7pool_del(env, identifier):
    """Deletes the identified pool

    Identifier is L7Pool Id. NOT the UUID
    """
    mgr = SoftLayer.LoadBalancerManager(env.client)
    try:
        mgr.del_lb_l7_pool(identifier)
        click.secho("Success", fg='green')
    except SoftLayerAPIError as exception:
        click.secho("ERROR: {}".format(exception.faultString), fg='red')
