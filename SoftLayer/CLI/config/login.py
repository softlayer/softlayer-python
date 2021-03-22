"""Gets a temporary token for a user"""
# :license: MIT, see LICENSE for more details.
import configparser
import os.path


import click
import json
import requests

import SoftLayer
from SoftLayer import config
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.consts import USER_AGENT
from SoftLayer import utils


@click.command()
@environment.pass_env
def cli(env):

    email = env.input("Email:")
    password = env.getpass("Password:")

    account_id = ''
    ims_id = ''
    print("ENV CONFIG FILE IS {}".format(env.config_file))
    sl_config = config.get_config(env.config_file)
    tokens = {'access_token': sl_config['softlayer']['access_token'], 'refresh_token': sl_config['softlayer']['refresh_token']}
    client = SoftLayer.API.IAMClient(config_file=env.config_file)
    user = client.authenticate_with_iam_token(tokens['access_token'], tokens['refresh_token'])
    print(user)
    # tokens = client.authenticate_with_password(email, password)

    # tokens = login(email, password)
    # print(tokens)
    


    accounts = get_accounts(tokens['access_token'])
    print(accounts)

    # if accounts.get('total_results', 0) == 1:
    #     selected = accounts['resources'][0]
    #     account_id = utils.lookup(selected, 'metadata', 'guid')
    #     ims_id = None
    #     for links in utils.lookup(selected, 'metadata', 'linked_accounts'):
    #         if links.get('origin') == "IMS":
    #             ims_id = links.get('id')

    #     print("Using account {}".format(utils.lookup(selected, 'entity', 'name')))
    #     tokens = refresh_token(tokens['refresh_token'], account_id, ims_id)
    #     print(tokens)

    # print("Saving Tokens...")

    
    for key in sl_config['softlayer']:
        print("{} = {} ".format(key, sl_config['softlayer'][key]))

    # sl_config['softlayer']['access_token'] = tokens['access_token']
    # sl_config['softlayer']['refresh_token'] = tokens['refresh_token']
    # sl_config['softlayer']['ims_account'] = ims_id
    # sl_config['softlayer']['account_id'] = account_id
    # config.write_config(sl_config, env.config_file)
    # print(sl_config)

    # print("Email: {}, Password: {}".format(email, password))

    print("Checking for an API key")
    
    user = client.call('SoftLayer_Account', 'getCurrentUser')
    print(user)



def get_accounts(a_token):
    """Gets account list from accounts.cloud.ibm.com/v1/accounts"""
    iam_client = requests.Session()

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': USER_AGENT,
        'Accept': 'application/json'
    }
    headers['Authorization'] = 'Bearer {}'.format(a_token)
    response = iam_client.request(
        'GET',
        'https://accounts.cloud.ibm.com/v1/accounts',
        headers=headers
    )

    response.raise_for_status()
    return json.loads(response.text)
