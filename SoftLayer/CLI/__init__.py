"CLI utilities"
import sys
import os.path
from pkgutil import iter_modules
from importlib import import_module
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


class Environment(object):

    # {'module_name': {'action': 'actionClass'}}
    plugins = {}

    def load_module(self, mod):  # pragma: no cover
        try:
            m = import_module('SoftLayer.CLI.%s' % mod)
            return m
        except ImportError:
            print("Error: Module '%s' does not exist!" % mod)
            raise CLIHalt(code=1)

    def add_plugin(self, cls):
        command = cls.__module__.split('.')[-1]
        if command not in self.plugins:
            self.plugins[command] = {}
        self.plugins[command][cls.action] = cls

    def plugin_list(self):
        actions = [action[1] for action in iter_modules(__path__)]
        return actions


class CLIRunnableType(type):

    env = Environment()

    def __init__(cls, name, bases, attrs):
        super(CLIRunnableType, cls).__init__(name, bases, attrs)
        if cls.env and name != 'CLIRunnable':
            cls.env.add_plugin(cls)


class CLIRunnable(object):
    __metaclass__ = CLIRunnableType
    action = None

    @staticmethod
    def add_additional_args(parser):
        pass

    @staticmethod
    def execute(client, args):
        pass


class Table(object):
    def __init__(self, columns):
        self.columns = columns
        self.rows = []
        self.align = {}
        self.format = {}
        self.sortby = None

    def add_row(self, row, **kwargs):
        self.rows.append(TableRow(row, **kwargs))

    def _col_format_mapping(self):
        " Generate mapping of column index to formatter for that column "
        format_col_map = {}
        for col, fmter in self.format.items():
            if col in self.columns:
                format_col_map[self.columns.index(col)] = fmter
        return format_col_map

    def prettytable(self, format=True):
        " Returns a new prettytable instance"
        t = PrettyTable(self.columns)
        if format and self.sortby:
            t.sortby = self.sortby
        if format:
            for a_col, alignment in self.align.items():
                t.align[a_col] = alignment

            # Generate mapping of column_id to formatter
            format_col_map = self._col_format_mapping()
        # Adding rows
        for row in self.rows:
            _row = list(row.items)

            if format:
                # format based on column formatters
                for fmt_i, fmter in row.formatters.items():
                    _row[fmt_i] = fmter(_row[fmt_i])

                # format based on row-specific formatters
                for fmt_i, fmter in format_col_map.items():
                    _row[fmt_i] = fmter(_row[fmt_i])

            t.add_row(_row)
        return t


class TableRow(object):
    def __init__(self, items, formatters=None):
        self.items = items
        self.formatters = formatters or {}


def format_output(data, fmt='table'):
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
