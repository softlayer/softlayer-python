"""
    SoftLayer.tests.CLI.core_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import logging

from SoftLayer.CLI import core
from SoftLayer import testing

import click


class CoreTests(testing.TestCase):

    def test_load_all(self):
        recursive_subcommand_loader(core.cli, path='root')


def recursive_subcommand_loader(root, path=''):
    if getattr(root, 'list_commands', None) is None:
        return

    ctx = click.Context(root)

    for command in root.list_commands(ctx):
        new_root = root.get_command(ctx, command)
        new_path = '%s:%s' % (path, command)
        recursive_subcommand_loader(new_root, path=new_path)
        logging.info('loading %s', new_path)
