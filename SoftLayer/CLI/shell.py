"""
    SoftLayer.CLI.shell
    ~~~~~~~~~~~~~~~~~~~
    An interactive shell which exposes the CLI

    :license: MIT, see LICENSE for more details.
"""
from __future__ import print_function
from __future__ import unicode_literals
import shlex
import sys
import traceback

import click
from prompt_toolkit import completion
from prompt_toolkit import shortcuts

from SoftLayer.CLI import core

# pylint: disable=broad-except


def main(env):
    """Main entry-point for the shell."""
    exit_code = 0
    while True:
        try:
            line = shortcuts.get_input("(%s)> " % exit_code,
                                       completer=ShellCompleter())
            try:
                args = shlex.split(line)
            except ValueError as ex:
                print("Invalid Command: %s" % ex)
                continue

            core.main(args=args, obj=env)
        except SystemExit as ex:
            exit_code = ex.code
        except KeyboardInterrupt:
            exit_code = 1
        except EOFError:
            return
        except Exception:
            exit_code = 1
            traceback.print_exc(file=sys.stderr)


class ShellCompleter(completion.Completer):
    """Completer for the shell."""

    def get_completions(self, document, complete_event):
        """Returns an iterator of completions for the shell."""
        try:
            parts = shlex.split(document.text_before_cursor)
        except ValueError:
            return []

        return _click_generator(core.cli, parts)


def _click_generator(root, parts):
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
            yield completion.Completion(option, -len(incomplete))
