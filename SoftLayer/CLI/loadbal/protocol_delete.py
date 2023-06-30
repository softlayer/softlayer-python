"""Delete load balancer protocol."""
import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@click.option('--uuid', help="Load Balancer Uuid.")
@environment.pass_env
def cli(env, identifier, uuid):
    """delete a load balancer protocol."""

    mgr = SoftLayer.LoadBalancerManager(env.client)

    uuid_lb = mgr.get_lb(identifier)['uuid']

    protocol = mgr.delete_protocol(uuid_lb, uuid)

    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'
    table.add_row(['Id', protocol.get('id')])
    table.add_row(['UUI', protocol.get('uuid')])
    table.add_row(['Address', protocol.get('address')])
    table.add_row(['Type', SoftLayer.LoadBalancerManager.TYPE.get(protocol.get('type'))])
    table.add_row(['Description', protocol.get('description')])

    env.fout(table)
