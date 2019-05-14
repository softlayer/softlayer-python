"""Get details for a hardware device."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer import utils

from pprint import pprint as pp 

@click.command()
@click.argument('identifier')
@click.option('--start_date', '-s', type=click.STRING, required=True,
              help="Start Date e.g. 2019-03-04 (yyyy-MM-dd)")
@click.option('--end_date', '-e', type=click.STRING, required=True, 
              help="End Date e.g. 2019-04-02 (yyyy-MM-dd)")
@click.option('--summary_period', '-p', type=click.INT, default=3600, show_default=True,
              help="300, 600, 1800, 3600, 43200 or 86400 seconds")
@environment.pass_env
def cli(env, identifier, start_date, end_date, summary_period):
    hardware = SoftLayer.HardwareManager(env.client)
    data = hardware.get_bandwidth_data(identifier, start_date, end_date, summary_period)
    pp(data)