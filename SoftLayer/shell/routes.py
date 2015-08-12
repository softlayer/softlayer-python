"""
    SoftLayer.CLI.routes
    ~~~~~~~~~~~~~~~~~~~
    Routes for shell-specific commands

    :license: MIT, see LICENSE for more details.
"""

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
