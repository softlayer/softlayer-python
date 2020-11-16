"""Display the RIR contact information for your account."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.registration import RegistrationManager


@click.command()
@environment.pass_env
def cli(env):
    """Display the RIR contact information for your account.

    """
    mgr = RegistrationManager(env.client)
    result = mgr.get_registration_details()
    table = formatting.Table(['Id', 'Name', 'Email', 'Label', 'Address', 'Phone'])
    for contact in result:
        json_result = {}
        json_result['id'] = contact['id']
        for property_contact in contact['properties']:
            json_result[property_contact['propertyType']['keyName']] = (property_contact['value'])

        table.add_row([json_result.get('id'),
                       json_result.get('FIRST_NAME') + ' ' + json_result.get('LAST_NAME'),
                       json_result.get('INTERNAL_LABEL'),
                       json_result.get('EMAIL_ADDRESS'),
                       json_result.get('ADDRESS') + ' ' + json_result.get('CITY') + ' ' +
                       json_result.get('STATE') + ' ' + json_result.get('COUNTRY') + ' ' +
                       json_result.get('POSTAL_CODE'),
                       json_result.get("PHONE")])
    env.fout(table)
