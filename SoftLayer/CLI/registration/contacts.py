"""Get Contact details for a subnet registration."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@environment.pass_env
def cli(env):
    """Display the RIR contact information for your account.

    """
    mgr = SoftLayer.NetworkManager(env.client)
    result = mgr.get_registration_details()
    table = formatting.Table(['id', 'name', 'email', 'label', 'address', 'phone'])
    for contact in result:
        json_result = {'EMAIL_ADDRESS': '', 'INTERNAL_LABEL': ''}
        json_result['id'] = contact['id']
        for property_contact in contact['properties']:
            if property_contact['propertyType']['keyName'] == 'EMAIL_ADDRESS':
                json_result['EMAIL_ADDRESS'] = property_contact['value']
                continue
            elif property_contact['propertyType']['keyName'] == 'INTERNAL_LABEL':
                json_result['INTERNAL_LABEL'] = property_contact['value']
                continue
            json_result[property_contact['propertyType']['keyName']] = (property_contact['value'])

        table.add_row([json_result['id'],
                       json_result['FIRST_NAME'] + ' ' + json_result['LAST_NAME'],
                       json_result['INTERNAL_LABEL'],
                       json_result['EMAIL_ADDRESS'],
                       json_result['ADDRESS'] + ' ' + json_result['CITY'] + ' ' +
                       json_result['STATE'] + ' ' + json_result['COUNTRY'] + ' ' +
                       json_result['POSTAL_CODE'],
                       json_result["PHONE"]])
    env.fout(table)
