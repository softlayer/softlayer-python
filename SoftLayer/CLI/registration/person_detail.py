"""Shows the contact information for a person."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.registration import ContactPerson
from SoftLayer.managers.registration import RegistrationManager


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Shows the contact information for a person."""

    tables = []
    registration_manager = RegistrationManager(env.client)
    contact_detail = registration_manager.get_contact_properties(identifier)
    contact_detail_table = get_contact_detail_table(contact_detail)
    tables.append(contact_detail_table)

    registration_details = registration_manager.get_registration_details(identifier)
    registered_subnets_table = get_registered_subnets_table(registration_details, contact_detail)
    tables.append(registered_subnets_table)
    env.fout(tables)


def get_contact_detail_table(registration_details):
    """Formats the Contacts Table"""
    table = formatting.KeyValueTable(['Field', 'Value'])
    table.title = 'Contact Details'
    table.align['Field'] = 'r'
    table.align['Value'] = 'l'
    for registration_detail in registration_details:
        key_name = registration_detail.get('propertyType', {}).get('keyName')
        value = registration_detail.get('value')
        table.add_row([key_name, value])
    return table


def get_registered_subnets_table(subnet_details, registration_details):
    """Formats the Subnets Table"""
    table = formatting.KeyValueTable(['Subnet', 'Person', 'Status', 'Notes'])
    table.title = 'Registered Subnets'
    person = ContactPerson({'properties':registration_details})
    for subnet_detail in subnet_details:
        cidr = subnet_detail.get('registration', {}).get('cidr')
        network = subnet_detail.get('registration', {}).get('networkIdentifier')
        subnet = "{}/{}".format(network, cidr)
        status = subnet_detail.get('registration', {}).get('status', {}).get('name')
        notes = subnet_detail.get('notes', '-')
        table.add_row([subnet, str(person), status, notes])

    return table
