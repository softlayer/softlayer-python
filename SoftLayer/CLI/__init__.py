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

# plugins is a hash of module name to a dict of actions names to action classes
plugins = {}


def add_plugin(cls):
    command = cls.__module__.split('.')[-1]
    if command not in plugins:
        plugins[command] = {}
    plugins[command][cls.action] = cls


def load_module(mod):  # pragma: no cover
    try:
        m = import_module('SoftLayer.CLI.%s' % mod)
        return m
    except ImportError:
        print("Error: Module '%s' does not exist!" % mod)
        raise CLIHalt(code=1)


class CLIRunnableType(type):
    def __init__(cls, name, bases, attrs):
        super(CLIRunnableType, cls).__init__(name, bases, attrs)
        if name != 'CLIRunnable':
            add_plugin(cls)


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


def action_list():
    actions = [action[1] for action in iter_modules(__path__)]
    return actions


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


class CLIHalt(SystemExit):
    def __init__(self, code=0, *args):
        super(CLIHalt, self).__init__(*args)
        self.code = code


def main():  # pragma: no cover
    # Parse Top-Level Arguments
    argv = sys.argv[1:]
    exit_status = 0
    try:
        module_name, parent_args, aux_args = \
            parse_primary_args(action_list(), argv)

        module = load_module(module_name)

        # Parse Module-Specific Arguments
        parsed_args = parse_module_args(
            module, module_name, plugins[module_name], parent_args.aux,
            aux_args)
        action = parsed_args.action

        if action not in plugins[module_name]:
            raise ValueError("No such method exists: %s" % action)

        # Parse Config
        config_files = ["~/.softlayer"]

        if parsed_args.config:
            config_files.append(parsed_args.config)

        client_params = parse_config(config_files)
        client = Client(**client_params)

        # Do the thing
        f = plugins[module_name][action]
        execute_action(f, client=client, args=parsed_args)
    except KeyboardInterrupt:
        exit_status = 1
    except SystemExit, e:
        exit_status = e.code
    except (SoftLayerError, Exception), e:
        print(e)
        exit_status = 1

    sys.exit(exit_status)


def execute_action(f, client=None, args=None):
    data = f.execute(client, args)
    if data:
        print(format_output(data, args))


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
