"""
    SoftLayer.helpers
    ~~~~~~~~~~~~~~~~~
    Helpers to be used in CLI modules in SoftLayer.CLI.modules.*

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
import os
import json
import ConfigParser
import StringIO

from SoftLayer.CLI.environment import CLIRunnableType
from SoftLayer.utils import NestedDict
from prettytable import PrettyTable, FRAME, NONE

__all__ = ['Table', 'KeyValueTable', 'CLIRunnable', 'FormattedItem',
           'valid_response', 'confirm', 'no_going_back', 'mb_to_gb', 'gb',
           'listing', 'CLIAbort', 'NestedDict', 'resolve_id', 'format_output',
           'update_with_template_args', 'FALSE_VALUES']

FALSE_VALUES = ['0', 'false', 'FALSE', 'no', 'False']


def format_output(data, fmt='table'):
    """ Given some data, will format it for output

    :param data: One of: String, Table, FormattedItem, List, Tuple,
                 SequentialOutput
    :param string fmt (optional): One of: table, raw, json, python
    """
    if isinstance(data, basestring):
        return data

    # responds to .prettytable()
    if hasattr(data, 'prettytable'):
        if fmt == 'table':
            return str(format_prettytable(data))
        elif fmt == 'raw':
            return str(format_no_tty(data))

    # responds to .to_python()
    if hasattr(data, 'to_python'):
        if fmt == 'json':
            return json.dumps(
                format_output(data, fmt='python'),
                indent=4,
                cls=CLIJSONEncoder)
        elif fmt == 'python':
            return data.to_python()

    # responds to .formatted
    if hasattr(data, 'formatted'):
        if fmt == 'table':
            return str(data.formatted)

    # responds to .separator
    if hasattr(data, 'separator'):
        output = [format_output(d, fmt=fmt) for d in data if d]
        return str(SequentialOutput(data.separator, output))

    # is iterable
    if isinstance(data, list) or isinstance(data, tuple):
        output = [format_output(d, fmt=fmt) for d in data]
        return format_output(listing(output, separator=os.linesep))

    # fallback, convert this odd object to a string
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
    for i, row in enumerate(table.rows):
        for j, item in enumerate(row):
            table.rows[i][j] = format_output(item, fmt='raw')
    t = table.prettytable()
    for col in table.columns:
        t.align[col] = 'l'
    t.hrules = NONE
    t.border = False
    t.header = False
    t.left_padding_width = 0
    t.right_padding_width = 2
    return t


class FormattedItem(object):
    def __init__(self, original, formatted=None):
        self.original = original
        if formatted is not None:
            self.formatted = formatted
        else:
            self.formatted = self.original

    def to_python(self):
        return self.original

    def __str__(self):
        if self.original is None:
            return 'NULL'
        return str(self.original)

    __repr__ = __str__


def mb_to_gb(megabytes):
    """ Takes in the number of megabytes and returns a FormattedItem that
        displays gigabytes.

    :param int megabytes: number of megabytes
    """
    return FormattedItem(megabytes, "%dG" % (float(megabytes) / 1024))


def gb(gigabytes):
    """ Takes in the number of gigabytes and returns a FormattedItem that
        displays gigabytes.

    :param int gigabytes: number of gigabytes
    """
    return FormattedItem(int(float(gigabytes)) * 1024,
                         "%dG" % int(float(gigabytes)))


def blank():
    """ Returns FormatedItem to make pretty output use a dash
        and raw formatting to use NULL
    """
    return FormattedItem(None, '-')


def listing(items, separator=','):
    """ Given an iterable, returns a FormatedItem which display a list of
        items

        :param items: An iterable that outputs strings
        :param string separator: the separator to use
    """
    return SequentialOutput(separator, items)


class CLIRunnable(object):
    __metaclass__ = CLIRunnableType
    options = []
    action = None

    @staticmethod
    def add_additional_args(parser):
        pass

    @staticmethod
    def execute(client, args):
        pass


def resolve_id(resolver, identifier, name='object'):
    """ Resolves a single id using an id resolver function which returns a list
        of ids.

    :param resolver: function that resolves ids. Should return None or a list
                     of ids.
    :param string identifier: a string identifier used to resolve ids
    :param string name: the object type, to be used in error messages

    """
    ids = resolver(identifier)

    if len(ids) == 0:
        raise CLIAbort("Error: Unable to find %s '%s'" % (name, identifier))

    if len(ids) > 1:
        raise CLIAbort(
            "Error: Multiple %s found for '%s': %s" %
            (name, identifier, ', '.join([str(_id) for _id in ids])))

    return ids[0]


def update_with_template_args(args):
    if args.get('--template'):
        if not os.path.exists(args['--template']):
            raise ArgumentError(
                'File does not exist [-t | --template] = %s'
                % args['--template'])

        config = ConfigParser.ConfigParser()
        ini_str = '[settings]\n' + open(
            os.path.expanduser(args.get('--template')), 'r').read()
        ini_fp = StringIO.StringIO(ini_str)
        config.readfp(ini_fp)

        # Merge template options with the options passed in
        for key, value in config.items('settings'):
            option_key = '--%s' % key
            if args.get(option_key) in [None, False]:
                args[option_key] = value


def valid_response(prompt, *valid):
    ans = raw_input(prompt).lower()

    if ans in valid:
        return True
    elif ans == '':
        return None

    return False


def confirm(prompt_str, default=False):
    if default:
        prompt = '%s [Y/n]: ' % prompt_str
    else:
        prompt = '%s [y/N]: ' % prompt_str

    response = valid_response(prompt, 'y', 'yes', 'yeah', 'yup', 'yolo')

    if response is None:
        return default

    return response


def no_going_back(confirmation):
    if not confirmation:
        confirmation = 'yes'

    return valid_response(
        'This action cannot be undone! '
        'Type "%s" or press Enter to abort: ' % confirmation,
        str(confirmation))


class CLIHalt(SystemExit):
    def __init__(self, code=0, *args):
        super(CLIHalt, self).__init__(*args)
        self.code = code


class CLIAbort(CLIHalt):
    def __init__(self, msg, *args):
        super(CLIAbort, self).__init__(code=2, *args)
        self.message = msg


class ArgumentError(CLIAbort):
    def __init__(self, msg, *args):
        super(CLIAbort, self).__init__(code=2, *args)
        self.message = "Argument Error: %s" % msg


class Table(object):
    def __init__(self, columns):
        self.columns = columns
        self.rows = []
        self.align = {}
        self.format = {}
        self.sortby = None

    def add_row(self, row):
        self.rows.append(row)

    def _format_python_value(self, value):
        if hasattr(value, 'to_python'):
            return value.to_python()
        return value

    def to_python(self):
        # Adding rows
        l = []
        for row in self.rows:
            formatted_row = [self._format_python_value(v) for v in row]
            l.append(dict(zip(self.columns, formatted_row)))
        return l

    def prettytable(self):
        """ Returns a new prettytable instance. """
        t = PrettyTable(self.columns)
        if self.sortby:
            t.sortby = self.sortby
        for a_col, alignment in self.align.items():
            t.align[a_col] = alignment

        # Adding rows
        for row in self.rows:
            t.add_row(row)
        return t


class KeyValueTable(Table):
    def to_python(self):
        d = {}
        for row in self.rows:
            d[row[0]] = self._format_python_value(row[1])
        return d


class SequentialOutput(list):
    def __init__(self, separator=os.linesep, *args, **kwargs):
        self.separator = separator
        super(SequentialOutput, self).__init__(*args, **kwargs)

    def to_python(self):
        return self

    def __str__(self):
        return self.separator.join(str(x) for x in self)


class CLIJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, FormattedItem):
            return obj.to_python()
        return super(CLIJSONEncoder, self).default(obj)
