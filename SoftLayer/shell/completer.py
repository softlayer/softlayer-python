"""
    SoftLayer.CLI.shell.completer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Click completer for prompt_toolkit

    :license: MIT, see LICENSE for more details.
"""
import shlex

import click
from prompt_toolkit import completion as completion

from SoftLayer.CLI import core


class ShellCompleter(completion.Completer):
    """Completer for the shell."""

    def get_completions(self, document, complete_event):
        """Returns an iterator of completions for the shell."""

        return _click_autocomplete(core.cli, document.text_before_cursor)


def _click_autocomplete(root, text):
    """Completer generator for click applications."""
    try:
        parts = shlex.split(text)
    except ValueError:
        return []

    location, incomplete = _click_resolve_command(root, parts)

    if not text.endswith(' ') and not incomplete and text:
        return []

    options = []
    if incomplete and not incomplete[0:2].isalnum():
        for param in location.params:
            if not isinstance(param, click.Option):
                continue
            options.extend(param.opts)
            options.extend(param.secondary_opts)
    elif isinstance(location, (click.MultiCommand, click.core.Group)):
        options.extend(location.list_commands(click.Context(location)))

    # collect options that starts with the incomplete section
    completions = []
    for option in options:
        if option.startswith(incomplete):
            completions.append(
                completion.Completion(option, -len(incomplete)))
    return completions


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
