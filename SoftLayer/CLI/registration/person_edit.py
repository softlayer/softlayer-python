"""Edit a Person's contact information"""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.exceptions import SoftLayerAPIError
from SoftLayer.CLI import formatting
from SoftLayer.managers.registration import RegistrationManager

# From SoftLayer_Account_Regional_Registry_Detail_Property_Type::getAllObjects()
PROPERTY_TYPES = {
    "FIRST_NAME": 2,
    "LAST_NAME": 3,
    "ADDRESS": 4,
    "CITY": 5,
    "STATE": 6,
    "POSTAL_CODE": 7,
    "COUNTRY": 8,
    "PHONE": 9,
    "FAX_NUMBER": 10,
    "EMAIL_ADDRESS": 11,
    "ORGANIZATION": 12,
    "COMMENTS": 13,
    "ABUSE_EMAIL": 14,
    "NETWORK_IDENTIFIER": 15,
    "NETWORK_NAME": 16,
    "DESCRIPTION": 17,
    "ADMINISTRATIVE_CONTACT": 18,
    "TECHNICAL_CONTACT": 19,
    "STATUS": 20,
    "ADDITIONAL_EMAIL": 41,
    "MAINTAINER": 42,
    "ADDITIONAL_MAINTAINER": 43,
    "DOMAINS_MAINTAINER": 44,
    "ROUTES_MAINTAINER": 45,
    "ABUSE_MAINTAINER": 46,
    "INTERNAL_LABEL": 61,
}

# Thanks https://stackoverflow.com/questions/50499340/specify-options-and-arguments-dynamically
def options_from_dict(options):
    def decorator(f):
        for opt_params in options.keys():
            opt_name = str.lower(opt_params)
            param_decls = ('--' + opt_name, opt_name)
            attrs = dict(required=False, type=str)
            click.option(*param_decls, **attrs)(f)
        return f
    return decorator


@click.command()
@click.argument('identifier')
@options_from_dict(PROPERTY_TYPES)
@environment.pass_env
def cli(env, *args, **kwargs):
    """Edit a Person's contact information. Any unspecified option remains unchanged."""
    from pprint import pprint as pp
    register_client = RegistrationManager(env.client)
    # pp(kwargs)

    # Get information about the person so we can check existing properties.
    person = register_client.get_registration_detail_object(kwargs['identifier'])
    pp(person)

    # Properties that don't exist need to be created, so we split out what needs to be done.
    to_edit = []
    to_create = []

    existing_properties = {}
    for prop in person['properties']:
        existing_properties[prop['propertyType']['keyName']] = prop['id']

    for option in kwargs:
        sl_option = str.upper(option)
        if kwargs[option] is not None and option != 'identifier':
            # The property exists, we need to edit it
            if sl_option in existing_properties.keys():
                to_edit.append({
                    'id': existing_properties.get(sl_option),
                    'value': kwargs.get(option),
                    'propertyType': {'keyName': sl_option}
                })
            # Property doesn't exist, need to create it.
            else:
                to_create.append({
                    'value': kwargs.get(option),
                    'propertyTypeId': PROPERTY_TYPES[sl_option],
                    'registrationDetailId': kwargs.get('identifier'),
                    'sequencePosition': 0 
                })

    try:
        if to_edit:
            register_client.edit_properties(to_edit)
            click.echo("Successfully edited properties.")
    except SoftLayerAPIError as ex:
        click.echo("Unable to edit properties: {}".format(ex))

    try:
        if to_create:
            register_client.create_properties(to_create)
            click.echo("Successfully created properties.")
    except SoftLayerAPIError as ex:
        click.echo("Unable to create new properties: {}".format(ex))
