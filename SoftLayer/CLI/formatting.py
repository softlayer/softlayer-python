"""
    SoftLayer.formatting
    ~~~~~~~~~~~~~~~~~~~~
    Provider classes and helper functions to display output onto a
    command-line.

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: MIT, see LICENSE for more details.
"""
import os
import json

from prettytable import PrettyTable, FRAME, NONE


def format_output(data, fmt='table'):
    """ Given some data, will format it for output

    :param data: One of: String, Table, FormattedItem, List, Tuple,
                 SequentialOutput
    :param string fmt (optional): One of: table, raw, json, python
    """
    if isinstance(data, basestring):
        if fmt == 'json':
            return json.dumps(data)
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
        if fmt == 'python':
            return output
        return format_output(listing(output, separator=os.linesep))

    # fallback, convert this odd object to a string
    return data


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


def active_txn(item):
    """ Returns a FormattedItem describing the active transaction (if any) on
        the given object. If no active transaction is running, returns a blank
        FormattedItem.

        :param item: An object capable of having an active transaction
    """
    if not item['activeTransaction']['transactionStatus']:
        return blank()

    return FormattedItem(
        item['activeTransaction']['transactionStatus'].get('name'),
        item['activeTransaction']['transactionStatus'].get('friendlyName'))


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
        if hasattr(obj, 'to_python'):
            return obj.to_python()
        return super(CLIJSONEncoder, self).default(obj)


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
