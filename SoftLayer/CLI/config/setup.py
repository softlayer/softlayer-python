"""Setup CLI configuration."""
# :license: MIT, see LICENSE for more details.
import webbrowser

import configparser
import json
import os.path
import requests

import click

import SoftLayer
from SoftLayer.CLI import config
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.consts import USER_AGENT
from SoftLayer import utils


def get_api_key(client, username, secret):  # pylint: disable=inconsistent-return-statements
    """Attempts API-Key and password auth to get an API key.

    This will also generate an API key if one doesn't exist
    """

    # Try to use a client with username/api key
    if len(secret) == 64 or username == 'apikey':
        try:
            client['Account'].getCurrentUser()
            return secret
        except SoftLayer.SoftLayerAPIError as ex:
            if 'invalid api token' not in ex.faultString.lower():
                raise
    else:
        if isinstance(client, SoftLayer.API.IAMClient):
            client.authenticate_with_iam_token(secret)
        else:
            # Try to use a client with username/password
            client.authenticate_with_password(username, secret)

        user_record = client.call('Account', 'getCurrentUser', mask='id, apiAuthenticationKeys')
        api_keys = user_record['apiAuthenticationKeys']
        if len(api_keys) == 0:
            return client.call('User_Customer', 'addApiAuthenticationKey', id=user_record['id'])
        return api_keys[0]['authenticationKey']


@click.command()
@click.option('-a', '--auth', type=click.Choice(['ibmid', 'cloud_key', 'classic_key', 'sso']),
              help="Select a method of authentication.", default='classic_key', show_default=True)
@environment.pass_env
def cli(env, auth):
    """Setup the ~/.softlayer file with username and apikey.

    [Auth Types]

    ibmid: Requires your cloud.ibm.com username and password, and generates a classic infrastructure API key.

    cloud_key: A 32 character API key. Username will be 'apikey'

    classic_key: A 64 character API key used in the Softlayer/Classic Infrastructure systems.

    sso: For users with @ibm.com email addresses.
    """
    username = None
    api_key = None

    timeout = 0
    defaults = config.get_settings_from_client(env.client)
    endpoint_url = get_endpoint_url(env, defaults.get('endpoint_url', 'public'))
    # Get ths username and API key
    if auth == 'ibmid':
        username, api_key = ibmid_login(env)

    elif auth == 'cloud_key':
        username = 'apikey'
        secret = env.getpass('Classic Infrastructue API Key', default=defaults['api_key'])
        new_client = SoftLayer.Client(username=username, api_key=secret, endpoint_url=endpoint_url, timeout=timeout)
        api_key = get_api_key(new_client, username, secret)

    elif auth == 'sso':
        username, api_key = sso_login(env)

    else:
        username = env.input('Classic Infrastructue Username', default=defaults['username'])
        secret = env.getpass('Classic Infrastructue API Key', default=defaults['api_key'])
        new_client = SoftLayer.Client(username=username, api_key=secret, endpoint_url=endpoint_url, timeout=timeout)
        api_key = get_api_key(new_client, username, secret)

    # Ask for timeout, convert to float, then to int
    timeout = int(float(env.input('Timeout', default=defaults['timeout'] or 0)))

    path = '~/.softlayer'
    if env.config_file:
        path = env.config_file
    config_path = os.path.expanduser(path)

    env.out(env.fmt(config.config_table({'username': username,
                                         'api_key': api_key,
                                         'endpoint_url': endpoint_url,
                                         'timeout': timeout})))

    if not formatting.confirm('Are you sure you want to write settings to "%s"?' % config_path, default=True):
        raise exceptions.CLIAbort('Aborted.')

    # Persist the config file. Read the target config file in before
    # setting the values to avoid clobbering settings
    parsed_config = configparser.RawConfigParser()
    parsed_config.read(config_path)
    try:
        parsed_config.add_section('softlayer')
    except configparser.DuplicateSectionError:
        pass

    parsed_config.set('softlayer', 'username', username)
    parsed_config.set('softlayer', 'api_key', api_key)
    parsed_config.set('softlayer', 'endpoint_url', endpoint_url)
    parsed_config.set('softlayer', 'timeout', timeout)

    config_fd = os.fdopen(os.open(config_path, (os.O_WRONLY | os.O_CREAT | os.O_TRUNC), 0o600), 'w')
    try:
        parsed_config.write(config_fd)
    finally:
        config_fd.close()

    env.fout("Configuration Updated Successfully")


def get_endpoint_url(env, endpoint='public'):
    """Gets the Endpoint to use."""

    endpoint_type = env.input('Endpoint (public|private|custom)', default=endpoint)
    endpoint_type = endpoint_type.lower()

    if endpoint_type == 'public':
        endpoint_url = SoftLayer.API_PUBLIC_ENDPOINT
    elif endpoint_type == 'private':
        endpoint_url = SoftLayer.API_PRIVATE_ENDPOINT
    else:
        if endpoint_type == 'custom':
            endpoint_url = env.input('Endpoint URL', default=endpoint)
        else:
            endpoint_url = endpoint_type
    return endpoint_url


def ibmid_login(env):
    """Uses an IBMid and Password to get an access token, and that access token to get an API key"""
    email = env.input("Email").strip()
    password = env.getpass("Password").strip()

    client = SoftLayer.API.IAMClient(config_file=env.config_file)

    # STEP 1: Get the base IAM Token with a username/password
    tokens = client.authenticate_with_password(email, password)

    # STEP 2: Figure out which account we want to use
    account = get_accounts(env, tokens['access_token'])

    # STEP 3: Refresh Token, using a specific account this time.
    tokens = client.refresh_iam_token(tokens['refresh_token'], account['account_id'], account['ims_id'])

    # STEP 4: Get or create the Classic Infrastructure API key
    user = client.call('SoftLayer_Account', 'getCurrentUser', mask="mask[id,username,apiAuthenticationKeys]")

    if len(user.get('apiAuthenticationKeys', [])) == 0:
        env.fout("Creating a Classic Infrastrucutre API key for {}".format(user['username']))
        api_key = client.call('User_Customer', 'addApiAuthenticationKey', id=user['id'])
    else:
        api_key = user['apiAuthenticationKeys'][0]['authenticationKey']

    return user.get('username'), api_key


def get_accounts(env, a_token):
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

    accounts = json.loads(response.text)
    selected = None
    ims_id = None
    if accounts.get('total_results', 0) == 1:
        selected = accounts['resources'][0]
    else:
        env.fout("Select an Account...")
        counter = 1
        for selected in accounts.get('resources', []):
            links = utils.lookup(selected, 'metadata', 'linked_accounts') or []
            for link in links:
                if link.get('origin') == "IMS":
                    ims_id = link.get('id')
            if ims_id is None:
                ims_id = "Unlinked"
            env.fout("{}: {} ({})".format(counter, utils.lookup(selected, 'entity', 'name'), ims_id))
            counter = counter + 1
        ims_id = None  # Reset ims_id to avoid any mix-match or something.
        choice = click.prompt('Enter a number', type=int)
        # Test to make sure choice is not out of bounds...
        selected = accounts['resources'][choice - 1]

    account_id = utils.lookup(selected, 'metadata', 'guid')
    links = utils.lookup(selected, 'metadata', 'linked_accounts') or []
    for link in links:
        if link.get('origin') == "IMS":
            ims_id = link.get('id')

    print("Using account {}".format(utils.lookup(selected, 'entity', 'name')))
    return {"account_id": account_id, "ims_id": ims_id}


def get_sso_url():
    """Gets the URL for using SSO Tokens"""

    iam_client = requests.Session()

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': USER_AGENT,
        'Accept': 'application/json'
    }
    response = iam_client.request(
        'GET',
        'https://iam.cloud.ibm.com/identity/.well-known/openid-configuration',
        headers=headers
    )

    response.raise_for_status()
    data = json.loads(response.text)
    return data.get('passcode_endpoint')


def sso_login(env):
    """Uses a SSO token to get a SL apikey"""
    passcode_url = get_sso_url()
    env.fout("Get a one-time code from {} to proceed.".format(passcode_url))
    open_browser = env.input("Open the URL in the default browser? [Y/n]", default='Y')
    if open_browser.lower() == 'y':
        webbrowser.open(passcode_url)
    passcode = env.input("One-time code")
    client = SoftLayer.API.IAMClient(config_file=env.config_file)

    # STEP 1: Get the base IAM Token with a username/password
    tokens = client.authenticate_with_passcode(passcode)

    # STEP 2: Figure out which account we want to use
    account = get_accounts(env, tokens['access_token'])

    # STEP 3: Refresh Token, using a specific account this time.
    tokens = client.refresh_iam_token(tokens['refresh_token'], account['account_id'], account['ims_id'])

    # STEP 4: Get or create the Classic Infrastructure API key
    # client.authenticate_with_iam_token(tokens['access_token'])
    user = client.call('SoftLayer_Account', 'getCurrentUser', mask="mask[id,username,apiAuthenticationKeys]")

    if len(user.get('apiAuthenticationKeys', [])) == 0:
        env.fout("Creating a Classic Infrastrucutre API key for {}".format(user['username']))
        api_key = client.call('User_Customer', 'addApiAuthenticationKey', id=user['id'])
    else:
        api_key = user['apiAuthenticationKeys'][0]['authenticationKey']
    return user.get('username'), api_key
