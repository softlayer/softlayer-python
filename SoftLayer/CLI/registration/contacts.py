"""Lists the People and Contacts that exist on this account."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.registration import ContactPerson
from SoftLayer.managers.registration import RegistrationManager


@click.command()
@environment.pass_env
def cli(env):
    """Lists the People and Contacts that exist on this account.

    Similar to the https://cloud.ibm.com/classic/network/rir/records page.
    """
    mgr = RegistrationManager(env.client)
    result = mgr.get_account_contacts()
    table = formatting.Table(['Id', 'Name', 'Label', 'Email', 'Address', 'Phone'])
    for contact in result:
        # Hopefully this class makes interacting with a Person contact easier.
        this_person = ContactPerson(contact)

        table.add_row([this_person.id,
                       this_person.get('FIRST_NAME') + ' ' + this_person.get('LAST_NAME'),
                       this_person.get('INTERNAL_LABEL', 'None'),
                       this_person.get('EMAIL_ADDRESS', 'None'),
                       this_person.get('ADDRESS') + ' ' + this_person.get('CITY') + ' ' +
                       this_person.get('STATE') + ' ' + this_person.get('COUNTRY') + ' ' +
                       this_person.get('POSTAL_CODE'),
                       this_person.get('PHONE')])
    env.fout(table)
