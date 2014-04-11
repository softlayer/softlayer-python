"""
usage: sl help [options]
       sl help <module> [options]
       sl help <module> <command> [options]

View help on a module or command.
"""
# :license: MIT, see LICENSE for more details.
# Missing docstrings ignored due to __doc__ = __doc__ magic
# pylint: disable=C0111

from SoftLayer.CLI.core import CommandParser
from SoftLayer.CLI import CLIRunnable


class Show(CLIRunnable):
    # Use the same documentation as the module
    __doc__ = __doc__
    action = None

    def execute(self, args):
        parser = CommandParser(self.env)
        if not any([args['<command>'], args['<module>']]):
            return parser.get_module_help('help')

        self.env.load_module(args['<module>'])

        if args['<command>']:
            return parser.get_command_help(args['<module>'], args['<command>'])
        elif args['<module>']:
            return parser.get_module_help(args['<module>'])
