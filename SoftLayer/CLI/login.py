"""Login with your employee username, password, 2fa token"""
# :license: MIT, see LICENSE for more details.

import click
import os 


from SoftLayer.API import EmployeeClient
from SoftLayer.CLI.command import SLCommand as SLCommand
from SoftLayer import config
from SoftLayer.CLI import environment


# def get_username(env):
#     """Gets the username from config or env"""
#     settings = 

def censor_password(value):
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
    settings = config.get_config(config_file=env.config_file)
    username = settings.get('username') or os.environ.get('SLCLI_USER')
    password = os.environ.get('SLCLI_PASSWORD', '')
    yubi = 123456

    url = settings.get('endpoint_url') or consts.API_EMPLOYEE_ENDPOINT
    click.echo("URL: {}".format(url))
    if username is None:
        username = input("Username: ")
    click.echo("Username: {}".format(username))
    if password is None:
        password = env.getpass("Password: ")
    click.echo("Password: {}".format(censor_password(password)))
    # yubi = input("Yubi: ")

    client = EmployeeClient(config_file=env.config_file)
    try:
        client.authenticate_with_password(username, password, yubi)
    except Exception as e:
        click.echo("EXCEPTION: {}".format(e))

    print("OK")
