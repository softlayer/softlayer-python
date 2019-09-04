"""List active Netscaler devices."""
import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils


@click.command()
@environment.pass_env
def cli(env):
    """List active Netscaler devices."""
    mgr = SoftLayer.LoadBalancerManager(env.client)

    netscalers = mgr.get_adcs()
    if netscalers:
        adc_table = generate_netscaler_table(netscalers)
        env.fout(adc_table)
    else:
        env.fout("No Netscalers")


def location_sort(location):
    """Quick function that just returns the datacenter longName for sorting"""
    return utils.lookup(location, 'datacenter', 'longName')


def generate_netscaler_table(netscalers):
    """Tales a list of SoftLayer_Network_Application_Delivery_Controller and makes a table"""
    table = formatting.Table([
        'Id', 'Location', 'Name', 'Description', 'IP Address', 'Management Ip', 'Bandwidth', 'Create Date'
    ], title="Netscalers")
    for adc in sorted(netscalers, key=location_sort):
        table.add_row([
            adc.get('id'),
            utils.lookup(adc, 'datacenter', 'longName'),
            adc.get('name'),
            adc.get('description'),
            adc.get('primaryIpAddress'),
            adc.get('managementIpAddress'),
            adc.get('outboundPublicBandwidthUsage', 0),
            utils.clean_time(adc.get('createDate'))
        ])
    return table
