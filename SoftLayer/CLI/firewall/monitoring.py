"""Get monitoring for a firewall device."""
# :license: MIT, see LICENSE for more details.
import datetime

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Gets bandwidth details for a firewall from the past 30 days."""

    mgr = SoftLayer.FirewallManager(env.client)

    _firewall = mgr.get_instance(identifier)

    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'

    end = datetime.date.today()
    start = end.replace(day=1)
    last_month = start - datetime.timedelta(days=30)

    monitoring = mgr.get_summary(_firewall['metricTrackingObject']['id'],
                                 last_month.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
    public_out = 0
    public_in = 0
    for monitor in monitoring:

        if monitor['type'] == 'publicOut_net_octet':
            public_out += monitor['counter']

        if monitor['type'] == 'publicIn_net_octet':
            public_in += monitor['counter']

    table.add_row(['Id', _firewall.get('id')])
    table.add_row(['Name', _firewall['networkGateway']['name']])
    table.add_row(['Stard Date', last_month.strftime('%Y-%m-%d')])
    table.add_row(['End Date', end.strftime('%Y-%m-%d')])
    table.add_row(['Out', formatting.b_to_gb(public_out)])
    table.add_row(['In', formatting.b_to_gb(public_in)])
    table.add_row(['Total', formatting.b_to_gb(public_out + public_in)])
    table.add_row(['Status', _firewall['networkGateway']['status']['name']])

    env.fout(table)
