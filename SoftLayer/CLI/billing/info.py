"""List BIlling information of Accounts."""
# :license: MIT, see LICENSE for more details.


import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils

import click


@click.command()
@environment.pass_env
def cli(env):
    """List billing information for accounts."""
    billing = SoftLayer.BillingManager(env.client)
    table = formatting.Table(['Name','Value'])
    info = billing.get_info()
    print info
    table.add_row(['id', info['id']])
    table.add_row(['paymentTerms', info['paymentTerms']])
    table.add_row(['modifyDate', info['modifyDate']])
    table.add_row(['anniversaryDayOfMonth', info['anniversaryDayOfMonth']])
    table.add_row(['lastFourPaymentCardDigits', info['lastFourPaymentCardDigits']])
    table.add_row(['cardExpirationMonth', info['cardExpirationMonth']])
    table.add_row(['cardExpirationYear', info['cardExpirationYear']])
    table.add_row(['percentDiscountOnetime', info['percentDiscountOnetime']])
    table.add_row(['sparePoolAmount', info['sparePoolAmount']])
    table.add_row(['lastPaymentDate', info['lastPaymentDate']])
    table.add_row(['createDate', info['createDate']])
    table.add_row(['percentDiscountRecurring', info['percentDiscountRecurring']])
    pass_table = formatting.Table(['Name', 'Value'])
    d = info['currency']
    print d
    for key in d.keys():
        print key, d[key]
        pass_table.add_row([key,d[key]])
    table.add_row(['currency',pass_table ])


    return table
