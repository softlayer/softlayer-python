"""Metric Utilities"""
from __future__ import print_function
import datetime
import itertools
import sys

import click
from SoftLayer import utils
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
import sparkblocks


def validate_datetime(ctx, param, value):
    try:
        return datetime.datetime.strptime(value, "%Y-%m-%d")
    except (ValueError, TypeError):
        pass

    try:
        return datetime.datetime.strptime(value, "%Y-%m-%d %H:%M%S")
    except (ValueError, TypeError):
        raise click.BadParameter(
            "not in the format 'YYYY-MM-DD' or 'YYYY-MM-DD HH-MM-SS'")


def _get_pooled_bandwidth(env, start, end):
    call = env.client.call('Account', 'getVirtualDedicatedRacks',
                           iter=True,
                           mask='id,name,metricTrackingObjectId')
    types = [
        {'keyName': 'PUBLICIN',
         'name': 'publicIn',
         'summaryType': 'sum'},
        {'keyName': 'PUBLICOUT',
         'name': 'publicOut',
         'summaryType': 'sum'},
        {'keyName': 'PRIVATEIN',
         'name': 'privateIn',
         'summaryType': 'sum'},
        {'keyName': 'PRIVATEOUT',
         'name': 'privateOut',
         'summaryType': 'sum'},
    ]

    with click.progressbar(list(call),
                           label='Calculating for bandwidth pools',
                           file=sys.stderr) as pools:
        for pool in pools:
            if not pool.get('metricTrackingObjectId'):
                continue

            yield {
                'id': pool['id'],
                'type': 'pool',
                'name': pool['name'],
                'data': env.client.call(
                    'Metric_Tracking_Object',
                    'getSummaryData',
                    start.strftime('%Y-%m-%d %H:%M:%S %Z'),
                    end.strftime('%Y-%m-%d %H:%M:%S %Z'),
                    types,
                    300,
                    id=pool['metricTrackingObjectId'],
                ),
            }


def _get_hardware_bandwidth(env, start, end):
    hw_call = env.client.call(
        'Account', 'getHardware',
        iter=True,
        mask='id,hostname,metricTrackingObject.id,'
             'virtualRack[id,bandwidthAllotmentTypeId]')
    types = [
        {'keyName': 'PUBLICIN',
         'name': 'publicIn',
         'summaryType': 'counter'},
        {'keyName': 'PUBLICOUT',
         'name': 'publicOut',
         'summaryType': 'counter'},
        {'keyName': 'PRIVATEIN',
         'name': 'privateIn',
         'summaryType': 'counter'},
        {'keyName': 'PRIVATEOUT',
         'name': 'privateOut',
         'summaryType': 'counter'},
    ]

    with click.progressbar(list(hw_call),
                           label='Calculating for hardware',
                           file=sys.stderr) as hws:
        for hw in hws:
            pool_name = None
            if utils.lookup(hw, 'virtualRack', 'bandwidthAllotmentTypeId') == 2:
                pool_name = utils.lookup(hw, 'virtualRack', 'name')

            yield {
                'id': hw['id'],
                'type': 'hardware',
                'name': hw['hostname'],
                'pool': pool_name,
                'data': env.client.call(
                    'Metric_Tracking_Object',
                    'getSummaryData',
                    start.strftime('%Y-%m-%d %H:%M:%S %Z'),
                    end.strftime('%Y-%m-%d %H:%M:%S %Z'),
                    types,
                    3600,
                    id=hw['metricTrackingObject']['id'],
                ),
            }


def _get_virtual_bandwidth(env, start, end):
    call = env.client.call(
        'Account', 'getVirtualGuests',
        iter=True,
        mask='id,hostname,metricTrackingObjectId,'
             'virtualRack[id,bandwidthAllotmentTypeId]')
    types = [
        {'keyName': 'PUBLICIN_NET_OCTET',
         'name': 'publicIn_net_octet',
         'summaryType': 'sum'},
        {'keyName': 'PUBLICOUT_NET_OCTET',
         'name': 'publicOut_net_octet',
         'summaryType': 'sum'},
        {'keyName': 'PRIVATEIN_NET_OCTET',
         'name': 'privateIn_net_octet',
         'summaryType': 'sum'},
        {'keyName': 'PRIVATEOUT_NET_OCTET',
         'name': 'privateOut_net_octet',
         'summaryType': 'sum'},
    ]

    with click.progressbar(list(call),
                           label='Calculating for virtual',
                           file=sys.stderr) as vms:
        for vm in vms:
            pool_name = None
            if utils.lookup(vm, 'virtualRack', 'bandwidthAllotmentTypeId') == 2:
                pool_name = utils.lookup(vm, 'virtualRack', 'id')

            yield {
                'id': vm['id'],
                'type': 'virtual',
                'name': vm['hostname'],
                'pool': pool_name,
                'data': env.client.call(
                    'Metric_Tracking_Object',
                    'getSummaryData',
                    start.strftime('%Y-%m-%d %H:%M:%S %Z'),
                    end.strftime('%Y-%m-%d %H:%M:%S %Z'),
                    types,
                    3600,
                    id=vm['metricTrackingObjectId'],
                ),
            }


@click.command(short_help="Bandwidth report for every pool/server")
@click.option(
    '--start',
    callback=validate_datetime,
    default=(datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d'),
    help="datetime in the format 'YYYY-MM-DD' or 'YYYY-MM-DD HH-MM-SS'")
@click.option(
    '--end',
    callback=validate_datetime,
    default=datetime.datetime.now().strftime('%Y-%m-%d'),
    help="datetime in the format 'YYYY-MM-DD' or 'YYYY-MM-DD HH-MM-SS'")
@environment.pass_env
def cli(env, start, end):
    """Bandwidth report for every pool/server. This reports on the total data
       transfered for each virtual sever, hardware server and bandwidth pool."""

    env.err('Generating bandwidth report for %s to %s' % (start, end))

    table = formatting.Table([
        'type',
        'name',
        'public_in',
        'public_out',
        'private_in',
        'private_out',
        'pool',
    ])

    def filter_data(key, results):
        return (result['counter'] for result in results
                if result['type'] == key)

    try:
        for item in itertools.chain(_get_pooled_bandwidth(env, start, end),
                                    _get_virtual_bandwidth(env, start, end),
                                    _get_hardware_bandwidth(env, start, end)):
            pub_in = int(sum(filter_data('publicIn_net_octet', item['data'])))
            pub_out = int(sum(filter_data('publicOut_net_octet', item['data'])))
            priv_in = int(sum(filter_data('privateIn_net_octet', item['data'])))
            priv_out = int(sum(filter_data('privateOut_net_octet', item['data'])))
            table.add_row([
                item['type'],
                item['name'],
                formatting.FormattedItem(formatting.b_to_gb(pub_in), pub_in),
                formatting.FormattedItem(formatting.b_to_gb(pub_out), pub_out),
                formatting.FormattedItem(formatting.b_to_gb(priv_in), priv_in),
                formatting.FormattedItem(formatting.b_to_gb(priv_out), priv_out),
                item.get('pool') or formatting.blank(),
            ])
    except KeyboardInterrupt:
        env.err("Printing collected results and then aborting.")

    env.out(env.fmt(table))
