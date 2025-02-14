"""https://cloud.ibm.com/docs/CDN?topic=CDN-cdn-deprecation"""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer


@click.command(cls=SoftLayer.CLI.command.SLCommand, deprecated=True)
def cli():
    """https://cloud.ibm.com/docs/CDN?topic=CDN-cdn-deprecation"""
