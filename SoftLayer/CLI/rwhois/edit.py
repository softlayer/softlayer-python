"""Edit the RWhois data on the account."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions


@click.command()
@click.option('--abuse', help='Set the abuse email address')
@click.option('--address1', help='Update the address 1 field')
@click.option('--address2', help='Update the address 2 field')
@click.option('--city', help='Set the city name')
@click.option('--company', help='Set the company name')
@click.option('--country', help='Set the two-letter country code')
@click.option('--firstname', help='Update the first name field')
@click.option('--lastname', help='Update the last name field')
@click.option('--postal', help='Set the postal code field')
@click.option('--public/--private',
              default=None,
              help='Flags the address as a public or private residence.')
@click.option('--state', help='Set the two-letter state code')
@environment.pass_env
def cli(env, abuse, address1, address2, city, company, country, firstname,
        lastname, postal, public, state):
    """Edit the RWhois data on the account."""
    mgr = SoftLayer.NetworkManager(env.client)

    update = {
        'abuse_email': abuse,
        'address1': address1,
        'address2': address2,
        'company_name': company,
        'city': city,
        'country': country,
        'first_name': firstname,
        'last_name': lastname,
        'postal_code': postal,
        'state': state,
        'private_residence': public,
    }

    if public is True:
        update['private_residence'] = False
    elif public is False:
        update['private_residence'] = True

    check = [x for x in update.values() if x is not None]
    if not check:
        raise exceptions.CLIAbort(
            "You must specify at least one field to update.")

    mgr.edit_rwhois(**update)
