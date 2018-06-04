"""List Users."""
# :license: MIT, see LICENSE for more details.


import json

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import helpers


@click.command()
@click.argument('user')
@click.option('--template', '-t', required=True,
              help="A json string describing https://softlayer.github.io/reference/datatypes/SoftLayer_User_Customer/")
@environment.pass_env
def cli(env, user, template):
    """Edit a Users details

    JSON strings should be enclosed in '' and each item should be enclosed in ""

    :Example: slcli user edit-details testUser -t '{"firstName": "Test", "lastName": "Testerson"}'
    """
    mgr = SoftLayer.UserManager(env.client)
    user_id = helpers.resolve_id(mgr.resolve_ids, user, 'username')

    user_template = {}
    if template is not None:
        try:
            template_object = json.loads(template)
            for key in template_object:
                user_template[key] = template_object[key]
        except ValueError as ex:
            raise exceptions.ArgumentError("Unable to parse --template. %s" % ex)

    result = mgr.edit_user(user_id, user_template)
    if result:
        click.secho("%s updated successfully" % (user), fg='green')
    else:
        click.secho("Failed to update %s" % (user), fg='red')
