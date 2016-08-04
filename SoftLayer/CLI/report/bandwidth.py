"""Metric Utilities"""
from __future__ import print_function
import datetime
import itertools
import sys

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils


# pylint: disable=unused-argument
def _validate_datetime(ctx, param, value):
    try:
        return datetime.datetime.strptime(value, "%Y-%m-%d")
    except (ValueError, TypeError):
        pass

    try:
        return datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        raise click.BadParameter(
            "not in the format 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'")


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
        for instance in hws:
            if not utils.lookup(instance, 'metricTrackingObject', 'id'):
                continue

            pool_name = None
            if utils.lookup(instance,
                            'virtualRack',
                            'bandwidthAllotmentTypeId') == 2:
                pool_name = utils.lookup(instance, 'virtualRack', 'name')

            yield {
                'id': instance['id'],
                'type': 'hardware',
                'name': instance['hostname'],
                'pool': pool_name,
                'data': env.client.call(
                    'Metric_Tracking_Object',
                    'getSummaryData',
                    start.strftime('%Y-%m-%d %H:%M:%S %Z'),
                    end.strftime('%Y-%m-%d %H:%M:%S %Z'),
                    types,
                    3600,
                    id=instance['metricTrackingObject']['id'],
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
        for instance in vms:
            pool_name = None
            if utils.lookup(instance,
                            'virtualRack',
                            'bandwidthAllotmentTypeId') == 2:
                pool_name = utils.lookup(instance, 'virtualRack', 'id')

            yield {
                'id': instance['id'],
                'type': 'virtual',
                'name': instance['hostname'],
                'pool': pool_name,
                'data': env.client.call(
                    'Metric_Tracking_Object',
                    'getSummaryData',
                    start.strftime('%Y-%m-%d %H:%M:%S %Z'),
                    end.strftime('%Y-%m-%d %H:%M:%S %Z'),
                    types,
                    3600,
                    id=instance['metricTrackingObjectId'],
                ),
            }


@click.command(short_help="Bandwidth report for every pool/server")
@click.option(
    '--start',
    callback=_validate_datetime,
    default=(
        datetime.datetime.now() - datetime.timedelta(days=30)
    ).strftime('%Y-%m-%d'),
    help="datetime in the format 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'")
@click.option(
    '--end',
    callback=_validate_datetime,
    default=datetime.datetime.now().strftime('%Y-%m-%d'),
    help="datetime in the format 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'")
@click.option('--sortby', help='Column to sort by',
              default='hostname',
              show_default=True)
@environment.pass_env
def cli(env, start, end, sortby):
    """Bandwidth report for every pool/server.

    This reports on the total data transfered for each virtual sever, hardware
    server and bandwidth pool.
    """

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
    table.sortby = sortby

    def f_type(key, results):
        "Filter metric data by type"
        return (result['counter'] for result in results
                if result['type'] == key)

    try:
        for item in itertools.chain(_get_pooled_bandwidth(env, start, end),
                                    _get_virtual_bandwidth(env, start, end),
                                    _get_hardware_bandwidth(env, start, end)):
            pub_in = int(sum(f_type('publicIn_net_octet', item['data'])))
            pub_out = int(sum(f_type('publicOut_net_octet', item['data'])))
            pri_in = int(sum(f_type('privateIn_net_octet', item['data'])))
            pri_out = int(sum(f_type('privateOut_net_octet', item['data'])))
            table.add_row([
                item['type'],
                item['name'],
                formatting.b_to_gb(pub_in),
                formatting.b_to_gb(pub_out),
                formatting.b_to_gb(pri_in),
                formatting.b_to_gb(pri_out),
                item.get('pool') or formatting.blank(),
            ])
    except KeyboardInterrupt:
        env.err("Printing collected results and then aborting.")

    env.out(env.fmt(table))
