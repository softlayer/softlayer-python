"""
usage: sl <command> [<args>...]
       sl help <command>
       sl [-h | --help]

SoftLayer Command-line Client

The available commands are:
  firewall  Firewall rule and security management
  image     Manages compute and flex images
  ssl       Manages SSL
  cci       Manage, delete, order compute instances
  dns       Manage DNS
  config    View and edit configuration for this tool
  metadata  Get details about this machine. Also available with 'my' and 'meta'

See 'sl help <command>' for more information on a specific command.

To use most commands your SoftLayer username and api_key need to be configured.
The easiest way to do that is to use: 'sl config setup'
"""
import sys
import os
import os.path

from prettytable import FRAME, NONE
from docopt import docopt

from SoftLayer import Client, SoftLayerError
from SoftLayer.consts import VERSION
from SoftLayer.CLI.helpers import (
    Table, CLIAbort, FormattedItem, listing, ArgumentError)
from SoftLayer.CLI.environment import Environment, CLIRunnableType


def format_output(data, fmt='table'):
    if isinstance(data, basestring):
        return data

    if isinstance(data, Table):
        if fmt == 'table':
            return str(format_prettytable(data))
        elif fmt == 'raw':
            return str(format_no_tty(data))

    if fmt != 'raw' and isinstance(data, FormattedItem):
        return str(data.formatted)

    if isinstance(data, list) or isinstance(data, tuple):
        output = [format_output(d, fmt=fmt) for d in data]
        return format_output(listing(output, separator=os.linesep))

    return str(data)


def format_prettytable(table):
    for i, row in enumerate(table.rows):
        for j, item in enumerate(row):
            table.rows[i][j] = format_output(item)
    t = table.prettytable()
    t.hrules = FRAME
    t.horizontal_char = '.'
    t.vertical_char = ':'
    t.junction_char = ':'
    return t


def format_no_tty(table):
    t = table.prettytable()
    for col in table.columns:
        t.align[col] = 'l'
    t.hrules = NONE
    t.border = False
    t.header = False
    return t


def parse_main_args(args=sys.argv[1:]):
    arguments = docopt(__doc__, version=VERSION, argv=args, options_first=True)
    return arguments


def parse_module_args(module, args):

    arg_doc = module.__doc__ + """
Standard Options:
  -h --help  Show this screen
"""
    arguments = docopt(
        arg_doc, version=VERSION, argv=args, options_first=True)
    return arguments


def parse_submodule_args(submodule, args):
    default_format = 'raw'
    if sys.stdout.isatty():
        default_format = 'table'

    arg_doc = submodule.__doc__

    if 'confirm' in submodule.options:
        arg_doc += """
Prompt Options:
  -y, --really  Confirm all prompt actions
"""

    arg_doc += """
Standard Options:
  --format=ARG           Output format. [Options: table, raw] [Default: %s]
  -C FILE --config=FILE  Config file location. [Default: ~/.softlayer]
  -h --help              Show this screen
""" % default_format

    arguments = docopt(arg_doc, version=VERSION, argv=args)
    return arguments


def main(args=sys.argv[1:], env=Environment()):
    """
    Handle conditions in this order:

    sl [help] [(-h | --help)]                -> show main help
    sl help <command>                        -> show command-specific help
    sl <command> [(-h | --help)]             -> show command-specific help
    sl invalid_command                       -> show main help
    sl <command> <subcommand> (-h | --help)  -> show subcommand-specific help
    sl <command> <subcommand> [options]      -> execute subcommand
    """
    # Parse Top-Level Arguments
    CLIRunnableType.env = env
    exit_status = 0
    try:
        # handle `sl ...`
        main_args = parse_main_args(args)
        module_name = env.get_module_name(main_args['<command>'])

        # handle `sl help <command>`
        if module_name == 'help' and len(main_args['<args>']) > 0:
            module = env.load_module(main_args['<args>'][0])
            parse_module_args(module, ['--help', main_args['<args>'][0]])

        # handle `sl --help` and `sl invalidcommand`
        if module_name not in env.plugin_list():
            parse_main_args(['--help'])

        module = env.load_module(module_name)
        actions = env.plugins[module_name]

        # handle `sl <command> ...`
        module_args = parse_module_args(
            module, [module_name] + main_args['<args>'])
        action_name = module_args['<command>']

        # handle `sl <command> invalidcommand`
        if action_name not in actions:
            parse_module_args(module, ['--help', module_name, action_name])

        action = actions[action_name]

        # handle `sl <command> <subcommand> ...`
        submodule_args = parse_submodule_args(
            action, [module_name] + main_args['<args>'])

        # Parse Config
        config_files = ["~/.softlayer"]

        if submodule_args.get('--config'):
            config_files.append(submodule_args.get('--config'))

        env.load_config(config_files)
        client = Client(
            username=env.config.get('username'),
            api_key=env.config.get('api_key'),
            endpoint_url=env.config.get('endpoint_url'))

        # Do the thing
        data = action.execute(client, submodule_args)
        if data:
            format = submodule_args.get('--format')
            if format not in ['raw', 'table']:
                raise ArgumentError('Invalid Format "%s"' % format)
            s = format_output(data, fmt=format)
            if s:
                env.out(s)

    except (ValueError, KeyError):
        raise
    except KeyboardInterrupt:
        env.out('')
        exit_status = 1
    except CLIAbort, e:
        env.err(str(e.message))
        exit_status = e.code
    except SystemExit, e:
        exit_status = e.code
    except (SoftLayerError, Exception), e:
        env.err(str(e))
        exit_status = 1

    sys.exit(exit_status)
