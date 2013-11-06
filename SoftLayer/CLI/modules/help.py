"""
usage: sl help [options]
       sl help <module> [options]
       sl help <module> <command> [options]

View help on a module or command.
"""
# :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
# :license: MIT, see LICENSE for more details.

from SoftLayer.CLI.core import CommandParser
from SoftLayer.CLI import CLIRunnable


class Show(CLIRunnable):
    # Use the same documentation as the module
    __doc__ = __doc__
    action = None

    def execute(self, args):
        parser = CommandParser(self.env)
        self.env.load_module(args['<module>'])
        if args['<command>']:
            return parser.get_command_help(args['<module>'], args['<command>'])
        elif args['<module>']:
            return parser.get_module_help(args['<module>'])
        return parser.get_main_help()
