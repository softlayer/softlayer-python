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
    config_settings = config.get_config(config_file=env.config_file)
    settings = config_settings['softlayer']
    username = settings.get('username') or os.environ.get('SLCLI_USER', None)
    password = os.environ.get('SLCLI_PASSWORD', '')
    yubi = None
#    client = EmployeeClient(config_file=env.config_file)
    client = env.client

    # Might already be logged in, try and refresh token
    if settings.get('access_token') and settings.get('userid'):
        client.authenticate_with_hash(settings.get('userid'), settings.get('access_token'))
        try:
            employee = client.call('SoftLayer_User_Employee', 'getObject', id=settings.get('userid'), mask="mask[id,username]")
            print(employee)
            refresh = client.call('SoftLayer_User_Employee', 'refreshEncryptedToken', settings.get('access_token'), id=settings.get('userid'))
            print("REFRESH:\n{}\n".format(refresh))
            # we expect 2 results, a hash and a timeout 
            if len(refresh) > 1:
                for returned_data in refresh:
                    # Access tokens should be 188 characters, but just incase.
                    if len(returned_data) > 180:
                        settings['access_token'] = returned_data
            else:
                raise Exception("Got unexpected data. Expected 2 properties: {}".format(refresh))
            config_settings['softlayer'] = settings
            config.write_config(config_settings, env.config_file)
            return
        except Exception as ex:
            print("Error with Hash, try with password: {}".format(ex))


    url = settings.get('endpoint_url') or consts.API_EMPLOYEE_ENDPOINT
    click.echo("URL: {}".format(url))
    if username is None:
        username = input("Username: ")
    click.echo("Username: {}".format(username))
    if password is None:
        password = env.getpass("Password: ")
    click.echo("Password: {}".format(censor_password(password)))
    yubi = input("Yubi: ")

    
    try:
        result = client.authenticate_with_password(username, password, str(yubi))
        print(result)
    except Exception as e:
        click.echo("EXCEPTION: {}".format(e))

    print("OK")
