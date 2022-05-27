"""Login with your employee username, password, 2fa token"""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI.command import SLCommand as SLCommand
from SoftLayer.CLI import config
from SoftLayer.CLI import environment


@click.command(cls=SLCommand)
@environment.pass_env
def cli(env):
    """Logs you into the internal SoftLayer Network.

    username and password can be set in SL_USER and SL_PASSWORD env variables. You will be prompted for them otherwise.
    """

    print("OK")
