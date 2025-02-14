"""https://cloud.ibm.com/docs/CDN?topic=CDN-cdn-deprecation"""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting


@click.command(cls=SoftLayer.CLI.command.SLCommand, deprecated=True)
@environment.pass_env
def cli(env):
    """https://cloud.ibm.com/docs/CDN?topic=CDN-cdn-deprecation"""
    pass