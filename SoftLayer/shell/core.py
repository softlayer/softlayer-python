"""
    SoftLayer.CLI.shell
    ~~~~~~~~~~~~~~~~~~~
    An interactive shell which exposes the CLI

    :license: MIT, see LICENSE for more details.
"""
from __future__ import print_function
from __future__ import unicode_literals
import copy
import os
import shlex
import sys
import traceback

import click
from prompt_toolkit import completion as p_completion
from prompt_toolkit import history as p_history
from prompt_toolkit import shortcuts as p_shortcuts

from SoftLayer.CLI import core
from SoftLayer.CLI import environment

# pylint: disable=broad-except

ALL_ROUTES = [
    ('exit', 'SoftLayer.shell.cmd_exit:cli'),
    ('shell-help', 'SoftLayer.shell.cmd_help:cli'),
    ('env', 'SoftLayer.shell.cmd_env:cli'),
]

ALL_ALIASES = {
    '?': 'shell-help',
    'help': 'shell-help',
    'quit': 'exit',
}


class ShellExit(Exception):
    """Exception raised to quit the shell."""
    pass


@click.command()
@environment.pass_env
@click.pass_context
def cli(ctx, env):
    """Enters a shell for slcli."""

    # Set up prompt_toolkit settings
    app_path = click.get_app_dir('softlayer')
    if not os.path.exists(app_path):
        os.makedirs(os.path.dirname(app_path))
    history = p_history.FileHistory(os.path.join(app_path, 'history'))
    completer = ShellCompleter()

    # Set up the environment
    env = copy.deepcopy(env)
    env.load_modules_from_python(ALL_ROUTES)
    env.aliases.update(ALL_ALIASES)
    env.vars['global_args'] = ctx.parent.params
    env.vars['is_shell'] = True
    env.vars['last_exit_code'] = 0

    while True:
        try:
            line = p_shortcuts.get_input("(%s)> " % env.vars['last_exit_code'],
                                         completer=completer,
                                         history=history)
            try:
                args = shlex.split(line)
            except ValueError as ex:
                print("Invalid Command: %s" % ex)
                continue

            if not args:
                continue

            # Reset client so that --fixtures can be toggled on and off
            env.client = None

            core.main(args=list(get_env_args(env)) + args,
                      obj=env,
                      prog_name="",
                      reraise_exceptions=True)
        except SystemExit as ex:
            env.vars['last_exit_code'] = ex.code
        except KeyboardInterrupt:
            env.vars['last_exit_code'] = 1
        except EOFError:
            return
        except ShellExit:
            return
        except Exception as ex:
            env.vars['last_exit_code'] = 1
            traceback.print_exc(file=sys.stderr)


class ShellCompleter(p_completion.Completer):
    """Completer for the shell."""

    def get_completions(self, document, complete_event):
        """Returns an iterator of completions for the shell."""
        try:
            parts = shlex.split(document.text_before_cursor)
        except ValueError:
            return []

        return _click_autocomplete(core.cli, parts)


def _click_autocomplete(root, parts):
    """Completer generator for click applications."""
    location = root
    incomplete = ''
    for part in parts:
        incomplete = part

        if not part[0:2].isalnum():
            continue

        try:
            next_location = location.get_command(click.Context(location),
                                                 part)
            if next_location is not None:
                location = next_location
                incomplete = ''
        except AttributeError:
            break

    options = []
    if incomplete and not incomplete[0:2].isalnum():
        for param in location.params:
            if not isinstance(param, click.Option):
                continue
            options.extend(param.opts)
            options.extend(param.secondary_opts)
    elif isinstance(location, (click.MultiCommand, click.core.Group)):
        options.extend(location.list_commands(click.Context(location)))

    # yield all collected options that starts with the incomplete section
    for option in options:
        if option.startswith(incomplete):
            yield p_completion.Completion(option, -len(incomplete))


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
