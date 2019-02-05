"""Print help text."""
# :license: MIT, see LICENSE for more details.

import click
from click import formatting

from SoftLayer.CLI import core as cli_core
from SoftLayer.CLI import environment
from SoftLayer.shell import routes


@click.command()
@environment.pass_env
@click.pass_context
def cli(ctx, env):
    """Print shell help text."""
    env.out("Welcome to the SoftLayer shell.")
    env.out("")

    formatter = formatting.HelpFormatter()
    commands = []
    shell_commands = []
    for name in cli_core.cli.list_commands(ctx):
        command = cli_core.cli.get_command(ctx, name)
        if command.short_help is None:
            command.short_help = command.help
        details = (name, command.short_help)
        if name in dict(routes.ALL_ROUTES):
            shell_commands.append(details)
        else:
            commands.append(details)

    with formatter.section('Shell Commands'):
        formatter.write_dl(shell_commands)

    with formatter.section('Commands'):
        formatter.write_dl(commands)

    for line in formatter.buffer:
        env.out(line, newline=False)
