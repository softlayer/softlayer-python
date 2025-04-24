"""Login with your employee username, password, 2fa token"""
# :license: MIT, see LICENSE for more details.
import os

import click

from SoftLayer.CLI.command import SLCommand as SLCommand
from SoftLayer.CLI import environment
from SoftLayer import config


def censor_password(value):
    """Replaces a password with *s"""
    if value:
        value = '*' * len(value)
    return value


@click.command(cls=SLCommand)
@environment.pass_env
def cli(env):
    """Logs you into the internal SoftLayer Network.

    username: Set this in either the softlayer config, or SL_USER ENV variable
    password: Set this in SL_PASSWORD env variable. You will be prompted for them otherwise.
    """
    config_settings = config.get_config(config_file=env.config_file)
    settings = config_settings['softlayer']
    username = settings.get('username') or os.environ.get('SLCLI_USER', None)
    password = os.environ.get('SLCLI_PASSWORD', '')
    yubi = None

    # Might already be logged in, try and refresh token
    if settings.get('access_token') and settings.get('userid'):
        env.client.authenticate_with_hash(settings.get('userid'), settings.get('access_token'))
        try:
            emp_id = settings.get('userid')
            env.client.call('SoftLayer_User_Employee', 'getObject', id=emp_id, mask="mask[id,username]")
            env.client.refresh_token(emp_id, settings.get('access_token'))
            env.client.call('SoftLayer_User_Employee', 'refreshEncryptedToken', settings.get('access_token'), id=emp_id)

            config_settings['softlayer'] = settings
            config.write_config(config_settings, env.config_file)
            return
        # pylint: disable=broad-exception-caught
        except Exception as ex:
            print("Error with Hash Authentication, try with password: {}".format(ex))

    url = settings.get('endpoint_url')
    click.echo("URL: {}".format(url))
    if username is None:
        username = input("Username: ")
    if not password:
        password = env.getpass("Password: ", default="")
    yubi = input("Yubi: ")

    try:
        result = env.client.authenticate_with_internal(username, password, str(yubi))
        print(result)
    # pylint: disable=broad-exception-caught
    except Exception as e:
        click.echo("EXCEPTION: {}".format(e))

    print("OK")
