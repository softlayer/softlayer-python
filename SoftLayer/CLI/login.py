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
@click.option('--session-token',
              default=None,
              help='An existing employee session token (hash). Click the "Copy Session Token" in the internal portal to get this value.'
                   'Can also be set via the SLCLI_SESSION_TOKEN environment variable.',
              envvar='SLCLI_SESSION_TOKEN')
@click.option('--user-id',
              default=None,
              type=int,
              help='Employee IMS user ID. This is the number in the url when you click your username in the internal portal, under "user information". '
                   'Can also be set via the SLCLI_USER_ID environment variable. Or read from the configuration file.',
              envvar='SLCLI_USER_ID')
@click.option('--legacy',
              default=False,
              type=bool,
              is_flag=True,
              help='Login with username, password, yubi key combination. Only valid if ISV is not required. If using ISV, use your session token.')
@environment.pass_env
def cli(env, session_token: str | None, user_id: int | None, legacy: bool):
    """Logs you into the internal SoftLayer Network.

    username: Set this in either the softlayer config, or SL_USER ENV variable
    password: Set this in SL_PASSWORD env variable. You will be prompted for them otherwise.

    To log in with an existing session token instead of username/password/2FA:

        slcli login --session-token <token> --user-id <id>

    Or via environment variables:

        SLCLI_SESSION_TOKEN=<token> SLCLI_USER_ID=<id> slcli login
    """
    config_settings = config.get_config(config_file=env.config_file)
    settings = config_settings['softlayer']

    if not user_id:
        user_id = int(settings.get('userid', 0))
    # --session-token supplied on the CLI (or via SLCLI_SESSION_TOKEN env var):
    # authenticate directly, persist to config, and return immediately.
    if session_token and not legacy:
        if not user_id:
            user_id = int(input("User ID (number): "))
        env.client.authenticate_with_hash(user_id, session_token)
        settings['access_token'] = session_token
        settings['userid'] = str(user_id)
        config_settings['softlayer'] = settings
        config.write_config(config_settings, env.config_file)
        click.echo("Logged in with session token for user ID {}.".format(user_id))
        return


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
