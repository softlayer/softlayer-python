"""Edit the RWhois data on the account"""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import image as image_mod
from SoftLayer import utils

import click


  # --abuse=EMAIL      Set the abuse email
  # --address1=ADDR    Update the address 1 field
  # --address2=ADDR    Update the address 2 field
  # --city=CITY        Set the city information
  # --company=NAME     Set the company name
  # --country=COUNTRY  Set the country information. Use the two-letter
  #                      abbreviation.
  # --firstname=NAME   Update the first name field
  # --lastname=NAME    Update the last name field
  # --postal=CODE      Set the postal code field
  # --private          Flags the address as a private residence.
  # --public           Flags the address as a public residence.
  # --state=STATE      Set the state information. Use the two-letter
  #                      abbreviation.
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

    mgr.edit_rwhois(**update)  # pylint: disable=W0142
