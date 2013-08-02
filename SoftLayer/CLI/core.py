"""
usage: sl <module> [<args>...]
       sl help <module>
       sl help <module> <command>
       sl [-h | --help]

SoftLayer Command-line Client

The available modules are:
  cci       Manage, delete, order compute instances
  config    View and edit configuration for this tool
  dns       Manage DNS
  firewall  Firewall rule and security management
  hardware  View hardware details
  bmetal    Interact with bare metal instances
  network   Perform various network operations
  help      Show help
  iscsi     View iSCSI details
  image     Manages compute and flex images
  metadata  Get details about this machine. Also available with 'my' and 'meta'
  nas       View NAS details
  ssl       Manages SSL

See 'sl help <module>' for more information on a specific module.

To use most commands your SoftLayer username and api_key need to be configured.
The easiest way to do that is to use: 'sl config setup'
"""
# :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
# :license: BSD, see LICENSE for more details.

import sys
import logging

from docopt import docopt, DocoptExit

from SoftLayer import Client, SoftLayerError, SoftLayerAPIError
from SoftLayer.consts import VERSION
from SoftLayer.CLI.helpers import CLIAbort, ArgumentError, format_output
from SoftLayer.CLI.environment import (
    Environment, CLIRunnableType, InvalidCommand, InvalidModule)


DEBUG_LOGGING_MAP = {
    '0': logging.CRITICAL,
    '1': logging.WARNING,
    '2': logging.INFO,
    '3': logging.DEBUG
}

VALID_FORMATS = ['raw', 'table', 'json']


class CommandParser(object):
    def __init__(self, env):
        self.env = env

    def get_main_help(self):
        return __doc__.strip()

    def get_module_help(self, module_name):
        module = self.env.load_module(module_name)
        arg_doc = module.__doc__
        return arg_doc.strip()

    def get_command_help(self, module_name, command_name):
        command = self.env.get_command(module_name, command_name)

        default_format = 'raw'
        if sys.stdout.isatty():
            default_format = 'table'

        arg_doc = command.__doc__

        if 'confirm' in command.options:
            arg_doc += """
Prompt Options:
  -y, --really  Confirm all prompt actions
"""

        if '[options]' in arg_doc:
            arg_doc += """
Standard Options:
  --format=ARG           Output format. [Options: table, raw] [Default: %s]
  -C FILE --config=FILE  Config file location. [Default: ~/.softlayer]
  --debug=LEVEL          Specifies the debug noise level
                           1=warn, 2=info, 3=debug
  -h --help              Show this screen
""" % default_format
        return arg_doc.strip()

    def parse_main_args(self, args):
        main_help = self.get_main_help()
        arguments = docopt(
            main_help,
            version=VERSION,
            argv=args,
            options_first=True)
        arguments['<module>'] = self.env.get_module_name(arguments['<module>'])
        return arguments

    def parse_module_args(self, module_name, args):
        arg_doc = self.get_module_help(module_name)
        arguments = docopt(
            arg_doc,
            version=VERSION,
            argv=[module_name] + args,
            options_first=True)
        module = self.env.load_module(module_name)
        return module, arguments

    def parse_command_args(self, module_name, command_name, args):
        command = self.env.get_command(module_name, command_name)
        arg_doc = self.get_command_help(module_name, command_name)
        arguments = docopt(arg_doc, version=VERSION, argv=[module_name] + args)
        return command, arguments

    def parse(self, args):
        # handle `sl ...`
        main_args = self.parse_main_args(args)
        module_name = main_args['<module>']

        # handle `sl <module> ...`
        module, module_args = self.parse_module_args(
            module_name, main_args['<args>'])

        # get the command argument
        command_name = module_args.get('<command>')

        # handle `sl <module> <command> ...`
        return self.parse_command_args(
            module_name,
            command_name,
            main_args['<args>'])


def main(args=sys.argv[1:], env=Environment()):
    """
    Entry point for the command-line client.
    """
    # Parse Top-Level Arguments
    CLIRunnableType.env = env
    exit_status = 0
    resolver = CommandParser(env)
    try:
        command, command_args = resolver.parse(args)

        # Set logging level
        debug_level = command_args.get('--debug')
        if debug_level:
            logger = logging.getLogger()
            h = logging.StreamHandler()
            logger.addHandler(h)
            logger.setLevel(DEBUG_LOGGING_MAP.get(debug_level, logging.DEBUG))

        # Parse Config
        config_files = ["~/.softlayer"]

        if command_args.get('--config'):
            config_files.append(command_args.get('--config'))

        env.load_config(config_files)
        client = Client(
            username=env.config.get('username'),
            api_key=env.config.get('api_key'),
            endpoint_url=env.config.get('endpoint_url'))

        # Do the thing
        data = command.execute(client, command_args)
        if data:
            format = command_args.get('--format', 'table')
            if format not in VALID_FORMATS:
                raise ArgumentError('Invalid format "%s"' % format)
            s = format_output(data, fmt=format)
            if s:
                env.out(s)

    except InvalidCommand, e:
        env.err(resolver.get_module_help(e.module_name))
        if e.command_name:
            env.err('')
            env.err(str(e))
            exit_status = 1
    except InvalidModule, e:
        env.err(resolver.get_main_help())
        if e.module_name:
            env.err('')
            env.err(str(e))
        exit_status = 1
    except DocoptExit as e:
        env.err(e.usage)
        env.err(
            '\nUnknown argument(s), use -h or --help for available options')
        exit_status = 127
    except KeyboardInterrupt:
        env.out('')
        exit_status = 1
    except CLIAbort as e:
        env.err(str(e.message))
        exit_status = e.code
    except SystemExit as e:
        exit_status = e.code
    except SoftLayerAPIError as e:
        if 'invalid api token' in e.faultString.lower():
            env.out("Authentication Failed: To update your credentials, use "
                    "'sl config setup'")
        else:
            env.err(str(e))
            exit_status = 1
    except SoftLayerError as e:
        env.err(str(e))
        exit_status = 1
    except Exception as e:
        import traceback
        env.err(traceback.format_exc())
        exit_status = 1

    sys.exit(exit_status)
