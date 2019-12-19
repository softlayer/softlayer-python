"""
    SoftLayer.CLI.shell.core
    ~~~~~~~~~~~~~~~~~~~~~~~~
    An interactive shell which exposes the CLI

    :license: MIT, see LICENSE for more details.
"""
import copy
import os
import shlex
import sys
import traceback

import click
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit import PromptSession

from SoftLayer.CLI import core
from SoftLayer.CLI import environment
from SoftLayer.shell import completer
from SoftLayer.shell import routes

# pylint: disable=broad-except


class ShellExit(Exception):
    """Exception raised to quit the shell."""


@click.command()
@environment.pass_env
@click.pass_context
def cli(ctx, env):
    """Enters a shell for slcli."""

    # Set up the environment
    env = copy.deepcopy(env)
    env.load_modules_from_python(routes.ALL_ROUTES)
    env.aliases.update(routes.ALL_ALIASES)
    env.vars['global_args'] = ctx.parent.params
    env.vars['is_shell'] = True
    env.vars['last_exit_code'] = 0

    # Set up prompt_toolkit settings
    app_path = click.get_app_dir('softlayer_shell')
    if not os.path.exists(app_path):
        os.makedirs(app_path)
    complete = completer.ShellCompleter(core.cli)

    session = PromptSession()

    while True:
        try:
            line = session.prompt(
                completer=complete,
                complete_while_typing=True,
                auto_suggest=AutoSuggestFromHistory(),
            )

            # Parse arguments
            try:
                args = shlex.split(line)
            except ValueError as ex:
                print("Invalid Command: %s" % ex)
                continue

            if not args:
                continue

            # Run Command
            try:
                # Reset client so that the client gets refreshed
                env.client = None
                core.main(args=list(get_env_args(env)) + args,
                          obj=env,
                          prog_name="",
                          reraise_exceptions=True)
            except SystemExit as ex:
                env.vars['last_exit_code'] = ex.code
            except EOFError:
                return
            except ShellExit:
                return
            except Exception:
                env.vars['last_exit_code'] = 1
                traceback.print_exc(file=sys.stderr)

        except KeyboardInterrupt:
            env.vars['last_exit_code'] = 130


def get_env_args(env):
    """Yield options to inject into the slcli command from the environment."""
    for arg, val in env.vars.get('global_args', {}).items():
        if val is True:
            yield '--%s' % arg
        elif isinstance(val, int):
            for _ in range(val):
                yield '--%s' % arg
        elif val is None:
            continue
        else:
            yield '--%s=%s' % (arg, val)
