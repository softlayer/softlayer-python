"""Command lines which modify power states."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier')
@environment.pass_env
def rescue(env, identifier):
    """Reboot into a rescue image."""

    vsi = SoftLayer.VSManager(env.client)
    vs_id = helpers.resolve_id(vsi.resolve_ids, identifier, 'VS')
    if not (env.skip_confirmations or
            formatting.confirm("This action will reboot this VSI. Continue?")):
        raise exceptions.CLIAbort('Aborted')

    vsi.rescue(vs_id)


@click.command()
@click.argument('identifier')
@click.option('--hard/--soft',
              default=None,
              help="Perform a hard or soft reboot")
@environment.pass_env
def reboot(env, identifier, hard):
    """Reboot an active virtual server."""

    virtual_guest = env.client['Virtual_Guest']
    mgr = SoftLayer.VSManager(env.client)
    vs_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'VS')
    if not (env.skip_confirmations or
            formatting.confirm('This will reboot the VS with id %s. '
                               'Continue?' % vs_id)):
        raise exceptions.CLIAbort('Aborted.')

    if hard is True:
        virtual_guest.rebootHard(id=vs_id)
    elif hard is False:
        virtual_guest.rebootSoft(id=vs_id)
    else:
        virtual_guest.rebootDefault(id=vs_id)


@click.command()
@click.argument('identifier')
@click.option('--hard/--soft', help="Perform a hard shutdown")
@environment.pass_env
def power_off(env, identifier, hard):
    """Power off an active virtual server."""

    virtual_guest = env.client['Virtual_Guest']
    vsi = SoftLayer.VSManager(env.client)
    vs_id = helpers.resolve_id(vsi.resolve_ids, identifier, 'VS')
    if not (env.skip_confirmations or
            formatting.confirm('This will power off the VS with id %s. '
                               'Continue?' % vs_id)):
        raise exceptions.CLIAbort('Aborted.')

    if hard:
        virtual_guest.powerOff(id=vs_id)
    else:
        virtual_guest.powerOffSoft(id=vs_id)


@click.command()
@click.argument('identifier')
@environment.pass_env
def power_on(env, identifier):
    """Power on a virtual server."""

    vsi = SoftLayer.VSManager(env.client)
    vs_id = helpers.resolve_id(vsi.resolve_ids, identifier, 'VS')
    env.client['Virtual_Guest'].powerOn(id=vs_id)


@click.command()
@click.argument('identifier')
@environment.pass_env
def pause(env, identifier):
    """Pauses an active virtual server."""

    vsi = SoftLayer.VSManager(env.client)
    vs_id = helpers.resolve_id(vsi.resolve_ids, identifier, 'VS')

    if not (env.skip_confirmations or
            formatting.confirm('This will pause the VS with id %s. Continue?'
                               % vs_id)):
        raise exceptions.CLIAbort('Aborted.')

    env.client['Virtual_Guest'].pause(id=vs_id)


@click.command()
@click.argument('identifier')
@environment.pass_env
def resume(env, identifier):
    """Resumes a paused virtual server."""

    vsi = SoftLayer.VSManager(env.client)
    vs_id = helpers.resolve_id(vsi.resolve_ids, identifier, 'VS')
    env.client['Virtual_Guest'].resume(id=vs_id)
