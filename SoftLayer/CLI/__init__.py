"CLI utilities"
import sys
import os.path
from pkgutil import iter_modules
from importlib import import_module
from copy import deepcopy
from argparse import ArgumentParser, SUPPRESS
from ConfigParser import SafeConfigParser

from prettytable import PrettyTable, FRAME, NONE

from SoftLayer import Client, SoftLayerError

__all__ = [
    'CLIRunnable',
    'Table',
    'confirm',
    'no_going_back',
]

plugins = {}


class CLIRunnableType(type):
    def __init__(cls, name, bases, attrs):
        super(CLIRunnableType, cls).__init__(name, bases, attrs)
        # print cls, name, bases, attrs
        if name != 'CLIRunnable':
            command = cls.__module__.split('.')[-1]
            if command not in plugins:
                plugins[command] = {}
            plugins[command][cls.action] = cls


class CLIRunnable(object):
    __metaclass__ = CLIRunnableType
    action = None

    @staticmethod
    def add_additional_args(parser):
        pass

    @staticmethod
    def execute(client, args):
        pass


class Table(PrettyTable):
    def __init__(self, *args, **kwargs):
        super(Table, self).__init__(*args, **kwargs)
        self.horizontal_char = '.'
        self.vertical_char = ':'
        self.junction_char = ':'


def format_output(data, args):
    if args.fmt == 'table':
        return format_prettytable(data)
    elif args.fmt == 'raw':
        return format_no_tty(data)


def format_prettytable(table):
    t = deepcopy(table)
    t.hrules = FRAME

    return t


def format_no_tty(table):
    notty = deepcopy(table)
    notty.hrules = NONE
    notty.border = False
    notty.header = False
    for k in notty.align.keys():
        notty.align[k] = 'l'
    return notty


def valid_response(prompt, *valid):
    ans = raw_input(prompt).lower()

    if ans in valid:
        return True
    elif ans == '':
        return None

    return False


def confirm(prompt_str="", allow_empty=False, default=False):
    fmt = (prompt_str, 'y', 'n') if default else (prompt_str, 'n', 'y')
    if allow_empty:
        prompt = '%s [%s]|%s: ' % fmt
    else:
        prompt = '%s %s|%s: ' % fmt

    response = valid_response(prompt, 'y', 'yes')

    if response is None and allow_empty:
        return default

    return response


def no_going_back(confirmation):
    if not confirmation:
        confirmation = 'yes'

    return valid_response(
        'This action cannot be undone! '
        'Type in "%s" or press Enter to abort.' % confirmation,
        confirmation)


def add_really_argument(parser):
    parser.add_argument(
        '--really', '-y',
        help='Confirm all prompt actions',
        action='store_true',
        default=False)


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


def action_list():
    actions = [action[1] for action in iter_modules(__path__)]
    return actions


def load_module(mod):  # pragma: no cover
    try:
        m = import_module('SoftLayer.CLI.%s' % mod)
        return m
    except ImportError:
        print("Error: Module '%s' does not exist!" % mod)
        sys.exit(1)


def main():  # pragma: no cover
    cli_args = sys.argv[1:]
    # Set up the primary parser. e.g. sl command
    parser = ArgumentParser(
        add_help=False,
        description='SoftLayer Command-line Client')
    actions = action_list()
    parser.add_argument(
        'module',
        help="Module name, try help or list",
        choices=[
            'help',
            'list',
        ] + actions, nargs='?')
    parser.add_argument('aux', nargs='*', help=SUPPRESS)
    add_fmt_argument(parser)

    parent_args, aux_args = parser.parse_known_args(args=cli_args)
    if parent_args.module is None:
        mod = 'help'
    else:
        mod = parent_args.module.lower()

    if mod == 'help':
        parser.print_help()
        sys.exit(1)

    module = load_module(mod)

    # If there are no command actions, run execute() on the module if it exists
    if len(parent_args.aux) == 0:
        try:
            data = module.execute(parent_args)
            if data:
                print(format_output(data, parent_args))
            sys.exit(0)
        except AttributeError:
            pass

    # Set up sub-command parser. e.g. sl command action
    parser = ArgumentParser(description=module.__doc__)
    parser.add_argument(mod)

    parser.add_argument('--config', '-C', help='Config file')
    add_fmt_argument(parser)

    methods = plugins[mod]

    if len(methods) > 0:
        action_parser = parser.add_subparsers(
            dest='action', description=module.__doc__)

        for keys, method in methods.iteritems():
            subparser = action_parser.add_parser(
                method.action,
                help=method.__doc__,
                description=method.__doc__,
            )
            method.add_additional_args(subparser)

    parsed_args = parser.parse_args(args=cli_args)
    action = parsed_args.action

    if action not in methods:
        raise ValueError("No such method exists: %s" % action)

    # Get config
    client_params = {}
    config_files = ["~/.softlayer"]

    if parsed_args.config:
        config_files.append(parsed_args.config)

    try:
        client_params = parse_config(config_files)
    except ValueError, e:
        if parsed_args.config:
            print(e)

    # Do the work
    try:
        client = Client(**client_params)
        data = methods[action].execute(client, parsed_args)
    except SoftLayerError, e:
        print(e)
        sys.exit(1)

    # Format/Output data
    if data:
        print(format_output(data, parsed_args))


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
