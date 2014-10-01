"""
usage: sl <module> [<args>...]
       sl help <module>
       sl help <module> <command>
       sl [-h | --help]

SoftLayer Command-line Client {version}

The available modules are:

Compute:
  image     Manages compute and flex images
  metadata  Get details about this machine. Also available with 'my' and 'meta'
  server    Bare metal servers
  sshkey    Manage SSH keys on your account
  vs        Virtual Servers (formerly CCIs)

Networking:
  cdn        Content Delivery Network service management
  dns        Domain Name System
  firewall   Firewall rule and security management
  loadbal    Load Balancer management
  globalip   Global IP address management
  messaging  Message Queue Service
  rwhois     RWhoIs operations
  ssl        Manages SSL
  subnet     Subnet ordering and management
  vlan       Manage VLANs on your account

Storage:
  iscsi     View iSCSI details
  nas       View NAS details
  snapshot  iSCSI snapshots

General:
  config    View and edit configuration for this tool
  ticket    Manage account tickets
  summary   Display an overall summary of your account
  help      Show help

See 'sl help <module>' for more information on a specific module.

To use most commands your SoftLayer username and api_key need to be configured.
The easiest way to do that is to use: 'sl config setup'
"""
# :license: MIT, see LICENSE for more details.

# pylint: disable=W0703

import logging
import sys

import docopt

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer import consts


DEBUG_LOGGING_MAP = {
    '0': logging.CRITICAL,
    '1': logging.WARNING,
    '2': logging.INFO,
    '3': logging.DEBUG
}

VALID_FORMATS = ['raw', 'table', 'json']


def _append_common_options(arg_doc):
    """Append common options to the doc string"""
    default_format = 'raw'
    if sys.stdout.isatty():
        default_format = 'table'

    arg_doc += """
Standard Options:
  --format=ARG            Output format. [Options: table, raw] [Default: %s]
  -C FILE --config=FILE   Config file location. [Default: ~/.softlayer]
  --debug=LEVEL           Specifies the debug noise level
                           1=warn, 2=info, 3=debug
  --timings               Time each API call and display after results
  --proxy=PROTO:PROXY_URL HTTP[s] proxy to be use to make API calls
  -h --help               Show this screen
""" % default_format
    return arg_doc


class CommandParser(object):
    """Helper class to parse commands.

    :param env: Environment instance
    """
    def __init__(self, env):
        self.env = env

    def get_main_help(self):
        """Get main help text."""
        main_doc = __doc__.format(version=SoftLayer.__version__)
        return _append_common_options(main_doc).strip()

    def get_module_help(self, module_name):
        """Get help text for a module."""
        module = self.env.load_module(module_name)
        arg_doc = module.__doc__
        return _append_common_options(arg_doc).strip()

    def get_command_help(self, module_name, command_name):
        """Get help text for a specific command."""
        command = self.env.get_command(module_name, command_name)
        arg_doc = command.__doc__

        if 'confirm' in command.options:
            arg_doc += """
Prompt Options:
  -y, --really  Confirm all prompt actions
"""

        return _append_common_options(arg_doc).strip()

    def parse_main_args(self, args):
        """Parse root arguments."""
        main_help = self.get_main_help()
        arguments = docopt.docopt(
            main_help,
            version=consts.VERSION,
            argv=args,
            options_first=True)
        arguments['<module>'] = self.env.get_module_name(arguments['<module>'])
        return arguments

    def parse_module_args(self, module_name, args):
        """Parse module arguments."""
        arg_doc = self.get_module_help(module_name)
        arguments = docopt.docopt(
            arg_doc,
            version=consts.VERSION,
            argv=[module_name] + args,
            options_first=True)
        return arguments

    def parse_command_args(self, module_name, command_name, args):
        """Parse command arguments."""
        command = self.env.get_command(module_name, command_name)
        arg_doc = self.get_command_help(module_name, command_name)
        arguments = docopt.docopt(arg_doc,
                                  version=consts.VERSION,
                                  argv=[module_name] + args)
        return command, arguments

    def parse(self, args):
        """Parse entire tree of arguments."""
        # handle `sl ...`
        main_args = self.parse_main_args(args)
        module_name = main_args['<module>']

        # handle `sl <module> ...`
        module_args = self.parse_module_args(module_name, main_args['<args>'])

        # get the command argument
        command_name = module_args.get('<command>')

        # handle `sl <module> <command> ...`
        return self.parse_command_args(
            module_name,
            command_name,
            main_args['<args>'])


def main(args=sys.argv[1:], env=environment.Environment()):
    """Entry point for the command-line client."""
    # Parse Top-Level Arguments
    exit_status = 0
    resolver = CommandParser(env)
    try:
        command, command_args = resolver.parse(args)

        # Set logging level
        debug_level = command_args.get('--debug')
        if debug_level:
            logger = logging.getLogger()
            handler = logging.StreamHandler()
            logger.addHandler(handler)
            logger.setLevel(DEBUG_LOGGING_MAP.get(debug_level, logging.DEBUG))

        kwargs = {
            'proxy': command_args.get('--proxy'),
            'config_file': command_args.get('--config')
        }
        if command_args.get('--timings'):
            client = SoftLayer.TimedClient(**kwargs)
        else:
            client = SoftLayer.Client(**kwargs)

        # Do the thing
        runnable = command(client=client, env=env)
        data = runnable.execute(command_args)
        if data:
            out_format = command_args.get('--format', 'table')
            if out_format not in VALID_FORMATS:
                raise exceptions.ArgumentError('Invalid format "%s"'
                                               % out_format)
            output = formatting.format_output(data, fmt=out_format)
            if output:
                env.out(output)

        if command_args.get('--timings'):
            out_format = command_args.get('--format', 'table')
            api_calls = client.get_last_calls()
            timing_table = formatting.KeyValueTable(['call', 'time'])

            for call, _, duration in api_calls:
                timing_table.add_row([call, duration])

            env.err(formatting.format_output(timing_table, fmt=out_format))

    except exceptions.InvalidCommand as ex:
        env.err(resolver.get_module_help(ex.module_name))
        if ex.command_name:
            env.err('')
            env.err(str(ex))
            exit_status = 1
    except exceptions.InvalidModule as ex:
        env.err(resolver.get_main_help())
        if ex.module_name:
            env.err('')
            env.err(str(ex))
        exit_status = 1
    except docopt.DocoptExit as ex:
        env.err(ex.usage)
        env.err(
            '\nUnknown argument(s), use -h or --help for available options')
        exit_status = 127
    except KeyboardInterrupt:
        env.out('')
        exit_status = 1
    except exceptions.CLIAbort as ex:
        env.err(str(ex.message))
        exit_status = ex.code
    except SystemExit as ex:
        exit_status = ex.code
    except SoftLayer.SoftLayerAPIError as ex:
        if 'invalid api token' in ex.faultString.lower():
            env.out("Authentication Failed: To update your credentials, use "
                    "'sl config setup'")
        else:
            env.err(str(ex))
            exit_status = 1
    except SoftLayer.SoftLayerError as ex:
        env.err(str(ex))
        exit_status = 1
    except Exception:
        import traceback
        env.err("An unexpected error has occured:")
        env.err(traceback.format_exc())
        env.err("Feel free to report this error as it is likely a bug:")
        env.err("    https://github.com/softlayer/softlayer-python/issues")
        exit_status = 1

    sys.exit(exit_status)
