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
@click.option('--frontend', '-f', required=True, default='HTTP:80', show_default=True, callback=parse_proto,
              help='PROTOCOL:PORT string for incoming internet connections.')
@click.option('--backend', '-b', required=True, default='HTTP:80', show_default=True, callback=parse_proto,
              help='PROTOCOL:PORT string for connecting to backend servers.')
@click.option('--method', '-m', help="Balancing Method.", default='ROUNDROBIN', show_default=True,
              type=click.Choice(['ROUNDROBIN', 'LEASTCONNECTION', 'WEIGHTED_RR']))
@click.option('--session', '-s', required=True,
              help="Session stickiness type. Valid values are SOURCE_IP or HTTP_COOKIE ")
@click.option('--max', help="Max Connections setting", type=int)
@environment.pass_env
def cli(env, identifier, **args):
    """Add a new load balancer protocol."""

    mgr = SoftLayer.LoadBalancerManager(env.client)

    uuid = mgr.get_lb_uuid(identifier)

    backend = args.get('backend')
    frontend = args.get('frontend')
    protocols = [
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

    protocol = mgr.add_protocols(uuid, protocols)

    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'
    table.add_row(['Id', protocol.get('id')])
    table.add_row(['UUI', protocol.get('uuid')])
    table.add_row(['Address', protocol.get('address')])
    table.add_row(['Type', mgr.get_lb_type(protocol.get('type'))])
    table.add_row(['Description', protocol.get('description')])

    env.fout(table)
