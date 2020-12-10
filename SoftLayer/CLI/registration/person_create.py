"""Create an additional contact"""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.managers.registration import RegistrationManager

# From SoftLayer_Account_Regional_Registry_Detail_Property_Type::getAllObjects()
PROPERTY_TYPES = {
    "COMMENTS": 13,
    "TECHNICAL_CONTACT": 19,
    "ADDITIONAL_EMAIL": 41,
    "PHONE": 9,
    "ABUSE_EMAIL": 14,
    "EMAIL_ADDRESS": 11,
    "POSTAL_CODE": 7,
    "STATE": 6,
    "COUNTRY": 8,
    "CITY": 5,
    "ADDRESS": 4,
    "LAST_NAME": 3,
    "FIRST_NAME": 2,
    "ORGANIZATION": 61,
}


# Thanks https://stackoverflow.com/questions/50499340/specify-options-and-arguments-dynamically
def options_from_dict(options):
    """Turns PROPERTY_TYPES into options for the CLI"""

    def decorator(deco_f):
        for opt_params in options.keys():
            opt_name = str.lower(opt_params)
            param_decls = ('--' + opt_name, opt_name)
            if opt_params == "ADDITIONAL_EMAIL" or opt_params == "TECHNICAL_CONTACT" or opt_params == "COMMENTS":
                attrs = dict(required=False, type=str)
            else:
                attrs = dict(required=True, type=str)
            click.option(*param_decls, **attrs)(deco_f)
        return deco_f

    return decorator


@click.command()
@options_from_dict(PROPERTY_TYPES)
@environment.pass_env
def cli(env, **kwargs):
    """Add Person Record

       Example::

       slcli reg person-create --organization "SoftLayer Internal - Development Community" --first_name TestName
       --last_name TestLastName --address "1234 Alpha Rd" --city Dallas --country US --state Texas
       --postal_code 4521-4123 --email_address test@ibm.com --abuse_email test2@ibm.com --phone 2717874571
       --comments Test
    """

    register_client = RegistrationManager(env.client)
    to_create = []

    for option in kwargs:
        sl_option = str.upper(option)
        if kwargs[option] is not None:
            to_create.append({
                'value': kwargs.get(option),
                'propertyTypeId': PROPERTY_TYPES[sl_option],
                'sequencePosition': 0
            })

    if not env.skip_confirmations:
        table = formatting.KeyValueTable(['name', 'value'])
        for option in kwargs:
            if kwargs[option] is not None:
                table.add_row([option, kwargs.get(option)])
        click.secho("You are about to create the following person record...", fg='green')
        env.fout(table)
        if not formatting.confirm("Do you wish to continue?"):
            raise exceptions.CLIAbort("Canceling creation!")

    template_object = {
        'detailTypeId': 3,  # SoftLayer_Account_Regional_Registry_Detail_Type::getAllObjects
                            # "id": 3, "keyName": "PERSON"
        'properties': to_create
    }

    result = register_client.create_person_record(template_object)

    table = formatting.KeyValueTable(['name', 'value'])
    table.add_row(["accountId", result['accountId']])
    table.add_row(["createDate", result['createDate']])
    table.add_row(["detailTypeId", result['detailTypeId']])
    table.add_row(["id", result['id']])
    env.fout(table)
