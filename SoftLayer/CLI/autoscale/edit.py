"""Edits an Autoscale group."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.managers.autoscale import AutoScaleManager


@click.command()
@click.argument('identifier')
# Suspend / Unsuspend
# Name
# Min/Max
# template->userData
# 'hostname', 'domain', 'startCpus', 'maxMemory', 'localDiskFlag'
# 'blockDeviceTemplateGroup.globalIdentifier
# blockDevices.diskImage.capacity
# sshKeys.id
# postInstallScriptUri
@environment.pass_env   
def cli(env, identifier):
    """Edits an Autoscale group."""

    autoscale = AutoScaleManager(env.client)
    groups = autoscale.details(identifier)
    click.echo(groups)
