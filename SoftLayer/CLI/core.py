"CLI utilities"
import sys
import os.path
from argparse import ArgumentParser, SUPPRESS
from ConfigParser import SafeConfigParser

from prettytable import FRAME, NONE

from SoftLayer import Client, SoftLayerError
from SoftLayer.CLI.helpers import Table, CLIHalt
from SoftLayer.CLI.environment import Environment, CLIRunnableType


def format_output(data, fmt='table'):
    if isinstance(data, basestring):
        return data
    if isinstance(data, Table):
        if fmt == 'table':
            return format_prettytable(data)
        elif fmt == 'raw':
            return format_no_tty(data)


def format_prettytable(table):
    t = table.prettytable(format=True)
    t.hrules = FRAME
    t.horizontal_char = '.'
    t.vertical_char = ':'
    t.junction_char = ':'
    return t


def format_no_tty(table):
    t = table.prettytable(format=False)
    for col in table.columns:
        t.align[col] = 'l'
    t.hrules = NONE
    t.border = False
    t.header = False
    return t


def add_config_argument(parser):
    parser.add_argument('--config', '-C', help='Config file', dest='config')


def add_fmt_argument(parser):
    fmt_default = 'raw'
    if sys.stdout.isatty():
        fmt_default = 'table'

    parser.add_argument(
        '--format',
        help='output format',
        choices=['table', 'raw'],
        default=fmt_default,
        dest='fmt')


def parse_primary_args(modules, argv):
    # Set up the primary parser. e.g. sl command
    description = 'SoftLayer Command-line Client'
    parser = ArgumentParser(description=description, add_help=False)

    parser.add_argument(
        'module',
        help="Module name",
        choices=sorted(['help'] + modules),
        default='help',
        nargs='?')
    parser.add_argument('aux', nargs='*', help=SUPPRESS)

    args, aux_args = parser.parse_known_args(args=argv)
    module_name = args.module.lower()

    if module_name == 'help':
        parser.print_help()
        raise CLIHalt(code=0)
    return module_name, args, aux_args


def parse_module_args(module, module_name, actions, posargs, argv):
    # Set up sub-command parser. e.g. sl command action
    args = posargs + argv

    parser = ArgumentParser(
        description=module.__doc__,
        prog="%s %s" % (os.path.basename(sys.argv[0]), module_name),
    )

    action_parser = parser.add_subparsers(dest='action')

    for action_name, method in actions.iteritems():
        if action_name:
            subparser = action_parser.add_parser(
                action_name,
                help=method.__doc__,
                description=method.__doc__,
            )
            method.add_additional_args(subparser)
            add_fmt_argument(subparser)
            add_config_argument(subparser)

    if len(posargs) == 0:
        parser.print_help()
        raise CLIHalt(code=0)

    return parser.parse_args(args=args)


def main(args=sys.argv[1:], env=Environment()):
    # Parse Top-Level Arguments
    CLIRunnableType.env = env
    exit_status = 0
    try:
        module_name, parent_args, aux_args = \
            parse_primary_args(env.plugin_list(), args)

        module = env.load_module(module_name)

        # Parse Module-Specific Arguments
        parsed_args = parse_module_args(
            module, module_name, env.plugins[module_name], parent_args.aux,
            aux_args)
        action = parsed_args.action

        # Parse Config
        config_files = ["~/.softlayer"]

        if parsed_args.config:
            config_files.append(parsed_args.config)

        client_params = parse_config(config_files)
        client = Client(**client_params)

        # Do the thing
        f = env.plugins[module_name][action]
        data = f.execute(client, parsed_args)
        if data:
            print(format_output(data, fmt=parsed_args.fmt))

    except KeyboardInterrupt:
        exit_status = 1
    except SystemExit, e:
        exit_status = e.code
    except (SoftLayerError, Exception), e:
        print(e)
        exit_status = 1

    sys.exit(exit_status)


def parse_config(files):
    config_files = [os.path.expanduser(f) for f in files]

    cp = SafeConfigParser({
        'username': '',
        'api_key': '',
        'endpoint_url': '',
    })
    cp.read(config_files)
    config = {}

    if not cp.has_section('softlayer'):
        return config

    for config_name in ['username', 'api_key', 'endpoint_url']:
        if cp.get('softlayer', config_name):
            config[config_name] = cp.get('softlayer', config_name)

    return config
