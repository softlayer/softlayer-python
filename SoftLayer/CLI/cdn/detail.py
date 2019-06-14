"""Detail a CDN Account."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@click.argument('unique_id')
@click.option('--history',
              default=30, type=click.IntRange(1, 89),
              help='Bandwidth, Hits, Ratio counted over history number of days ago. 89 is the maximum. ')
@environment.pass_env
def cli(env, unique_id, history):
    """Detail a CDN Account."""

    manager = SoftLayer.CDNManager(env.client)

    cdn_mapping = manager.get_cdn(unique_id)
    cdn_metrics = manager.get_usage_metrics(unique_id, history=history)

    # usage metrics
    total_bandwidth = "%s GB" % cdn_metrics['totals'][0]
    total_hits = cdn_metrics['totals'][1]
    hit_ratio = "%s %%" % cdn_metrics['totals'][2]

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
    table.add_row(['hit_radio', hit_ratio])

    env.fout(table)
