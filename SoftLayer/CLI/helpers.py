"""
    SoftLayer.helpers
    ~~~~~~~~~~~~~~~~~
    Helpers to be used in CLI modules in SoftLayer.CLI.modules.*

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
import os

from SoftLayer.CLI.environment import CLIRunnableType
from SoftLayer.utils import NestedDict
from prettytable import PrettyTable, FRAME, NONE

__all__ = ['Table', 'CLIRunnable', 'FormattedItem', 'valid_response',
           'confirm', 'no_going_back', 'mb_to_gb', 'gb', 'listing', 'CLIAbort',
           'NestedDict', 'resolve_id', 'format_output']


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

    if isinstance(data, SequentialOutput):
        output = [format_output(d, fmt=fmt) for d in data]
        if not data.blanks:
            output = [x for x in output if len(x)]
        return format_output(output, fmt=fmt)

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

    def __str__(self):
        return str(self.original)

    __repr__ = __str__


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


def mb_to_gb(megabytes):
    return FormattedItem(megabytes, "%dG" % (float(megabytes) / 1024))


def gb(gigabytes):
    return FormattedItem(int(float(gigabytes)) * 1024,
                         "%dG" % int(float(gigabytes)))


def blank():
    """ Returns FormatedItem to make pretty output use a dash
    and raw formatting to use NULL"""
    return FormattedItem('NULL', '-')


def listing(item, separator=','):
    l = separator.join((str(i) for i in item))
    return FormattedItem(l, l)


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


class SequentialOutput(list):
    def __init__(self, blanks=True, *args, **kwargs):
        self.blanks = blanks
