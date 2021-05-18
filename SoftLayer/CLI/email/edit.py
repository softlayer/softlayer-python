"""Edit details of an Delivery email account."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.managers.email import EmailManager


@click.command()
@click.argument('identifier')
@click.option('--username', help="Sets username for this account")
@click.option('--email', help="Sets the contact email for this account")
@click.option('--password',
              help="Password must be between 8 and 20 characters "
                   "and must contain one letter and one number.")
@environment.pass_env
def cli(env, identifier, username, email, password):
    """Edit details of an email delivery account."""
    email_manager = EmailManager(env.client)

    data = {}
    update = False
    if email:
        if email_manager.update_email(identifier, email):
            update = True
        else:
            raise exceptions.CLIAbort("Failed to Edit emailAddress account")
    if username:
        data['username'] = username
    if password:
        data['password'] = password
    if len(data) != 0:
        if email_manager.editObject(identifier, **data):
            update = True
        else:
            raise exceptions.CLIAbort("Failed to Edit email account")

    if update:
        env.fout('Updated Successfully')
