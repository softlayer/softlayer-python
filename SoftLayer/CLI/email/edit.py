"""Edit details of an Delivery email account."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.managers.email import EmailManager


@click.command()
@click.argument('identifier')
@click.option('--username', help="username account")
@click.option('--email', help="Additional note for the image")
@click.option('--password',
              help="Password must be between 8 and 20 characters "
                   "and must contain one letter and one number.")
@environment.pass_env
def cli(env, identifier, username, email, password):
    """Edit details of an email delivery account."""
    data = {}
    if username:
        data['username'] = username
    if email:
        data['emailAddress'] = email
    if password:
        data['password'] = password

    email_manager = EmailManager(env.client)

    if not email_manager.editObject(identifier, data):
        raise exceptions.CLIAbort("Failed to Edit email account")
