"""Power commands."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@click.option('--force', default=False, is_flag=True, help="Force modify")
@environment.pass_env
def power_off(env, identifier, force):
    """Power off an active server."""

    mgr = SoftLayer.HardwareManager(env.client)
    hw_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'hardware')
    if not force:
        if not (env.skip_confirmations or
                formatting.confirm('This will power off the server with id %s '
                                   'Continue?' % hw_id)):
            raise exceptions.CLIAbort('Aborted.')

    env.client['Hardware_Server'].powerOff(id=hw_id)


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@click.option('--hard/--soft',
              default=None,
              help="Perform a hard or soft reboot")
@environment.pass_env
def reboot(env, identifier, hard):
    """Reboot an active server."""

    hardware_server = env.client['Hardware_Server']
    mgr = SoftLayer.HardwareManager(env.client)
    hw_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'hardware')
    if not (env.skip_confirmations or
            formatting.confirm('This will power off the server with id %s. '
                               'Continue?' % hw_id)):
        raise exceptions.CLIAbort('Aborted.')

    if hard is True:
        hardware_server.rebootHard(id=hw_id)
    elif hard is False:
        hardware_server.rebootSoft(id=hw_id)
    else:
        hardware_server.rebootDefault(id=hw_id)


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@click.option('--force', default=False, is_flag=True, help="Force modify")
@environment.pass_env
def power_on(env, identifier, force):
    """Power on a server."""

    mgr = SoftLayer.HardwareManager(env.client)
    hw_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'hardware')

    if not force:
        if not (env.skip_confirmations or
                formatting.confirm('This will power off the server with id %s. '
                                   'Continue?' % hw_id)):
            raise exceptions.CLIAbort('Aborted.')

    env.client['Hardware_Server'].powerOn(id=hw_id)


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@environment.pass_env
def power_cycle(env, identifier):
    """Power cycle a server."""

    mgr = SoftLayer.HardwareManager(env.client)
    hw_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'hardware')

    if not (env.skip_confirmations or
            formatting.confirm('This will power off the server with id %s. '
                               'Continue?' % hw_id)):
        raise exceptions.CLIAbort('Aborted.')

    env.client['Hardware_Server'].powerCycle(id=hw_id)


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@environment.pass_env
def rescue(env, identifier):
    """Reboot server into a rescue image."""

    mgr = SoftLayer.HardwareManager(env.client)
    hw_id = helpers.resolve_id(mgr.resolve_ids, identifier, 'hardware')

    if not (env.skip_confirmations or
            formatting.confirm("This action will reboot this server. Continue?")):

        raise exceptions.CLIAbort('Aborted')

    env.client['Hardware_Server'].bootToRescueLayer(id=hw_id)
