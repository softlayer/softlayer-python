"""Creates a user """
# :license: MIT, see LICENSE for more details.

import json
import string
import sys

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


@click.command()
@click.argument('username')
@click.option('--email', '-e', required=True,
              help="Email address for this user. Required for creation.")
@click.option('--password', '-p', default=None, show_default=True,
              help="Password to set for this user. If no password is provided, user will be sent an email "
                   "to generate one, which expires in 24 hours.  '-p generate' will create a password for you "
                   "(Requires Python 3.6+). Passwords require 8+ characters, upper and lowercase, a number "
                   "and a symbol.")
@click.option('--from-user', '-u', default=None,
              help="Base user to use as a template for creating this user. "
                   "Will default to the user running this command. Information provided in --template "
                   "supersedes this template.")
@click.option('--template', '-t', default=None,
              help="A json string describing https://softlayer.github.io/reference/datatypes/SoftLayer_User_Customer/")
@click.option('--api-key', '-a', default=False, is_flag=True, help="Create an API key for this user.")
@environment.pass_env
def cli(env, username, email, password, from_user, template, api_key):
    """Creates a user Users.

    :Example: slcli user create my@email.com -e my@email.com -p generate -a
    -t '{"firstName": "Test", "lastName": "Testerson"}'

    Remember to set the permissions and access for this new user.
    """

    mgr = SoftLayer.UserManager(env.client)
    user_mask = ("mask[id, firstName, lastName, email, companyName, address1, city, country, postalCode, "
                 "state, userStatusId, timezoneId]")
    from_user_id = None
    if from_user is None:
        user_template = mgr.get_current_user(objectmask=user_mask)
        from_user_id = user_template['id']
    else:
        from_user_id = helpers.resolve_id(mgr.resolve_ids, from_user, 'username')
        user_template = mgr.get_user(from_user_id, objectmask=user_mask)
    # If we send the ID back to the API, an exception will be thrown
    del user_template['id']

    if template is not None:
        try:
            template_object = json.loads(template)
            for key in template_object:
                user_template[key] = template_object[key]
        except ValueError as ex:
            raise exceptions.ArgumentError("Unable to parse --template. %s" % ex)

    user_template['username'] = username
    if password == 'generate':
        password = generate_password()

    user_template['email'] = email

    if not env.skip_confirmations:
        table = formatting.KeyValueTable(['name', 'value'])
        for key in user_template:
            table.add_row([key, user_template[key]])
        table.add_row(['password', password])
        click.secho("You are about to create the following user...", fg='green')
        env.fout(table)
        if not formatting.confirm("Do you wish to continue?"):
            raise exceptions.CLIAbort("Canceling creation!")

    result = mgr.create_user(user_template, password)
    new_api_key = None
    if api_key:
        click.secho("Adding API key...", fg='green')
        new_api_key = mgr.add_api_authentication_key(result['id'])

    table = formatting.Table(['Username', 'Email', 'Password', 'API Key'])
    table.add_row([result['username'], result['email'], password, new_api_key])
    env.fout(table)


def generate_password():
    """Returns a 23 character random string, with 3 special characters at the end"""
    if sys.version_info > (3, 6):
        import secrets  # pylint: disable=import-error
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for i in range(20))
        special = ''.join(secrets.choice(string.punctuation) for i in range(3))
        return password + special
    else:
        raise ImportError("Generating passwords require python 3.6 or higher")
