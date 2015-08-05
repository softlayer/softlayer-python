"""Print help text."""
# :license: MIT, see LICENSE for more details.

import click
from click import formatting

from SoftLayer.CLI import core
from SoftLayer.CLI import environment


@click.command()
@environment.pass_env
@click.pass_context
def cli(ctx, env):
    """Print shell help text."""
    env.out("Welcome to the SoftLayer shell.")
    env.out("")

    formatter = formatting.HelpFormatter()
    commands = []
    for name in core.cli.list_commands(ctx):
        command = core.cli.get_command(ctx, name)
        commands.append((name, command.short_help))

    with formatter.section('Available Commands'):
        formatter.write_dl(commands)

    for line in formatter.buffer:
        env.out(line, newline=False)
