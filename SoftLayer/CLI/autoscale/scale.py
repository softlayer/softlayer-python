"""Scales an Autoscale group"""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.autoscale import AutoScaleManager
from SoftLayer import utils


@click.command()
@click.argument('identifier')
@click.option('--up/--down', 'scale_up', is_flag=True, default=True,
              help="'--up' adds guests, '--down' removes guests.")
@click.option('--by/--to', 'scale_by', is_flag=True, required=True,
              help="'--by' will add/remove the specified number of guests."
              " '--to' will add/remove a number of guests to get the group's guest count to the specified number.")
@click.option('--amount', required=True, type=click.INT, help="Number of guests for the scale action.")
@environment.pass_env
def cli(env, identifier, scale_up, scale_by, amount):
    """Scales an Autoscale group. Bypasses a scale group's cooldown period."""

    autoscale = AutoScaleManager(env.client)

    # Scale By, and go down, need to use negative amount
    if not scale_up and scale_by:
        amount = amount * -1

    result = []
    if scale_by:
        click.secho("Scaling group {} by {}".format(identifier, amount), fg='green')
        result = autoscale.scale(identifier, amount)
    else:
        click.secho("Scaling group {} to {}".format(identifier, amount), fg='green')
        result = autoscale.scale_to(identifier, amount)

    try:
        # Check if the first guest has a cancellation date, assume we are removing guests if it is.
        cancel_date = result[0]['virtualGuest']['billingItem']['cancellationDate'] or False
    except (IndexError, KeyError, TypeError):
        cancel_date = False

    if cancel_date:
        member_table = formatting.Table(['Id', 'Hostname', 'Created'], title="Cancelled Guests")
    else:
        member_table = formatting.Table(['Id', 'Hostname', 'Created'], title="Added Guests")

    for guest in result:
        real_guest = guest.get('virtualGuest')
        member_table.add_row([
            guest.get('id'), real_guest.get('hostname'), utils.clean_time(real_guest.get('createDate'))
        ])

    env.fout(member_table)
