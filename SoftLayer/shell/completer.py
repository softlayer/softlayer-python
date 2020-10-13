"""
    SoftLayer.CLI.shell.completer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Click completer for prompt_toolkit

    :license: MIT, see LICENSE for more details.
"""
import itertools
import shlex

import click
from prompt_toolkit import completion as completion


class ShellCompleter(completion.Completer):
    """Completer for the shell."""

    def __init__(self, click_root):
        self.root = click_root

    def get_completions(self, document, complete_event):
        """Returns an iterator of completions for the shell."""

        return _click_autocomplete(self.root, document.text_before_cursor)


def _click_autocomplete(root, text):
    """Completer generator for click applications."""
    try:
        parts = shlex.split(text)
    except ValueError:
        return

    location, incomplete = _click_resolve_command(root, parts)

    if not text.endswith(' ') and not incomplete and text:
        return

    if incomplete and not incomplete[0:2].isalnum():
        for param in location.params:
            if not isinstance(param, click.Option):
                continue
            for opt in itertools.chain(param.opts, param.secondary_opts):
                if opt.startswith(incomplete):
                    yield completion.Completion(opt, -len(incomplete), display_meta=param.help)

    elif isinstance(location, (click.MultiCommand, click.core.Group)):
        ctx = click.Context(location)
        commands = location.list_commands(ctx)
        for command in commands:
            if command.startswith(incomplete):
                cmd = location.get_command(ctx, command)
                yield completion.Completion(command, -len(incomplete), display_meta=cmd.short_help)


def _click_resolve_command(root, parts):
    """Return the click command and the left over text given some vargs."""
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
    return location, incomplete
