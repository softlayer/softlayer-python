"""Add a new load balancer protocol."""
import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting


# pylint: disable=unused-argument
def parse_proto(ctx, param, value):
    """Parses the frontend and backend cli options"""
    proto = {'protocol': 'HTTP', 'port': 80}
    splitout = value.split(':')
    if len(splitout) != 2:
        raise exceptions.ArgumentError("{}={} is not properly formatted.".format(param, value))
    proto['protocol'] = splitout[0]
    proto['port'] = int(splitout[1])
    return proto


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@click.option('--uuid', help="Load Balancer Uuid.")
@click.option('--frontend', '-f', required=True, default='HTTP:80', show_default=True, callback=parse_proto,
              help='PROTOCOL:PORT string for incoming internet connections.')
@click.option('--backend', '-b', required=True, default='HTTP:80', show_default=True, callback=parse_proto,
              help='PROTOCOL:PORT string for connecting to backend servers.')
@click.option('--method', '-m', help="Balancing Method.", default='ROUNDROBIN', show_default=True,
              type=click.Choice(['ROUNDROBIN', 'LEASTCONNECTION', 'WEIGHTED_RR']))
@click.option('--session', '-s', required=True,
              help="Session stickiness type. Valid values are “SOURCE_IP” “HTTP_COOKIE”")
@click.option('--max', help="Use a Public to Public loadbalancer.")
@environment.pass_env
def cli(env, identifier, **args):
    """Edit a load balancer protocol."""

    mgr = SoftLayer.LoadBalancerManager(env.client)

    uuid_lb = mgr.get_lb(identifier)['uuid']

    backend = args.get('backend')
    frontend = args.get('frontend')
    protocol_configurations = [
        {
            "backendPort": backend.get('port'),
            "backendProtocol": backend.get('protocol'),
            "frontendPort": frontend.get('port'),
            "frontendProtocol": frontend.get('protocol'),
            "loadBalancingMethod": args.get('method'),
            "sessionType": args.get('session'),
            "maxConn": args.get('max')
        }
    ]
    protocol_configurations[0]['listenerUuid'] = args.get('uuid')
    protocol = mgr.add_protocols(uuid_lb, protocol_configurations)

    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'
    table.add_row(['Id', protocol.get('id')])
    table.add_row(['UUI', protocol.get('uuid')])
    table.add_row(['Address', protocol.get('address')])
    table.add_row(['Type', SoftLayer.LoadBalancerManager.TYPE.get(protocol.get('type'))])
    table.add_row(['Description', protocol.get('description')])

    env.fout(table)
