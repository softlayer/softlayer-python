"""Detail a CDN Account."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@click.argument('unique_id')
@click.option('--last_days',
              default=30,
              help='cdn overview last days less than 90 days, because it is the maximum e.g 7, 15, 30, 60, 89')
@environment.pass_env
def cli(env, unique_id, last_days):
    """Detail a CDN Account."""

    manager = SoftLayer.CDNManager(env.client)

    cdn_mapping = manager.get_cdn(unique_id)
    cdn_metrics = manager.get_usage_metrics(unique_id, days=last_days)

    # usage metrics
    total_bandwidth = str(cdn_metrics['totals'][0]) + " GB"
    total_hits = str(cdn_metrics['totals'][1])
    hit_radio = str(cdn_metrics['totals'][2]) + " %"

    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'

    table.add_row(['unique_id', cdn_mapping['uniqueId']])
    table.add_row(['hostname', cdn_mapping['domain']])
    table.add_row(['protocol', cdn_mapping['protocol']])
    table.add_row(['origin', cdn_mapping['originHost']])
    table.add_row(['origin_type', cdn_mapping['originType']])
    table.add_row(['path', cdn_mapping['path']])
    table.add_row(['provider', cdn_mapping['vendorName']])
    table.add_row(['status', cdn_mapping['status']])
    table.add_row(['total_bandwidth', total_bandwidth])
    table.add_row(['total_hits', total_hits])
    table.add_row(['hit_radio', hit_radio])

    env.fout(table)
