"""
    SoftLayer.formatting
    ~~~~~~~~~~~~~~~~~~~~
    Provider classes and helper functions to display output onto a
    command-line.

    :license: MIT, see LICENSE for more details.
"""
# pylint: disable=E0202
import json
import os

import prettytable

from SoftLayer import utils

FALSE_VALUES = ['0', 'false', 'FALSE', 'no', 'False']


def format_output(data, fmt='table'):  # pylint: disable=R0911,R0912
    """Given some data, will format it for console output.

    :param data: One of: String, Table, FormattedItem, List, Tuple,
                 SequentialOutput
    :param string fmt (optional): One of: table, raw, json, python
    """
    if isinstance(data, utils.string_types):
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
    """Converts SoftLayer.CLI.formatting.Table instance to a prettytable."""
    for i, row in enumerate(table.rows):
        for j, item in enumerate(row):
            table.rows[i][j] = format_output(item)
    ptable = table.prettytable()
    ptable.hrules = prettytable.FRAME
    ptable.horizontal_char = '.'
    ptable.vertical_char = ':'
    ptable.junction_char = ':'
    return ptable


def format_no_tty(table):
    """Converts SoftLayer.CLI.formatting.Table instance to a prettytable."""
    for i, row in enumerate(table.rows):
        for j, item in enumerate(row):
            table.rows[i][j] = format_output(item, fmt='raw')
    ptable = table.prettytable()
    for col in table.columns:
        ptable.align[col] = 'l'
    ptable.hrules = prettytable.NONE
    ptable.border = False
    ptable.header = False
    ptable.left_padding_width = 0
    ptable.right_padding_width = 2
    return ptable


def mb_to_gb(megabytes):
    """Converts number of megabytes to a FormattedItem in gigabytes.

    :param int megabytes: number of megabytes
    """
    return FormattedItem(megabytes, "%dG" % (float(megabytes) / 1024))


def gb(gigabytes):  # pylint: disable=C0103
    """Converts number of gigabytes to a FormattedItem in gigabytes.

    :param int gigabytes: number of gigabytes
    """
    return FormattedItem(int(float(gigabytes)) * 1024,
                         "%dG" % int(float(gigabytes)))


def blank():
    """Returns a blank FormattedItem."""
    return FormattedItem(None, '-')


def listing(items, separator=','):
    """Given an iterable return a FormattedItem which display the list of items

        :param items: An iterable that outputs strings
        :param string separator: the separator to use
    """
    return SequentialOutput(separator, items)


def active_txn(item):
    """Returns a FormattedItem describing the active transaction on a object.

        If no active transaction is running, returns a blank FormattedItem.

        :param item: An object capable of having an active transaction
    """
    return transaction_status(item['activeTransaction'])


def transaction_status(transaction):
    """Returns a FormattedItem describing the given transaction.

        :param item: An object capable of having an active transaction
    """
    if not transaction.get('transactionStatus'):
        return blank()

    return FormattedItem(
        transaction['transactionStatus'].get('name'),
        transaction['transactionStatus'].get('friendlyName'))


def valid_response(prompt, *valid):
    """Prompt user for input.

    Will display a prompt for a command-line user. If the input is in the
    valid given valid list then it will return True. Otherwise, it will
    return False. If no input is received from the user, None is returned
    instead.

    :param string prompt: string prompt to give to the user
    :param string \\*valid: valid responses
    """
    ans = utils.console_input(prompt).lower()

    if ans in valid:
        return True
    elif ans == '':
        return None

    return False


def confirm(prompt_str, default=False):
    """Show a confirmation prompt to a command-line user.

    :param string prompt_str: prompt to give to the user
    :param bool default: Default value to True or False
    """
    if default:
        prompt = '%s [Y/n]: ' % prompt_str
    else:
        prompt = '%s [y/N]: ' % prompt_str

    response = valid_response(prompt, 'y', 'yes', 'yeah', 'yup', 'yolo')

    if response is None:
        return default

    return response


def no_going_back(confirmation):
    """Show a confirmation to a user.

    :param confirmation str: the string the user has to enter in order to
                             confirm their action.
    """
    if not confirmation:
        confirmation = 'yes'

    return valid_response(
        'This action cannot be undone! '
        'Type "%s" or press Enter to abort: ' % confirmation,
        str(confirmation))


class SequentialOutput(list):
    """SequentialOutput is used for outputting sequential items.

    The purpose is to de-couple the separator from the output itself.

    :param separator str: string to use as a default separator
    """
    def __init__(self, separator=os.linesep, *args, **kwargs):
        self.separator = separator
        super(SequentialOutput, self).__init__(*args, **kwargs)

    def to_python(self):
        """returns itself, since it itself is a list."""
        return self

    def __str__(self):
        return self.separator.join(str(x) for x in self)


class CLIJSONEncoder(json.JSONEncoder):
    """A JSON encoder which is able to use a .to_python() method on objects."""
    def default(self, obj):
        """Encode object if it implements to_python()."""
        if hasattr(obj, 'to_python'):
            return obj.to_python()
        return super(CLIJSONEncoder, self).default(obj)


class Table(object):
    """A Table structure used for output.

    :param list columns: a list of column names
    """
    def __init__(self, columns):
        self.columns = columns
        self.rows = []
        self.align = {}
        self.format = {}
        self.sortby = None

    def add_row(self, row):
        """Add a row to the table.

        :param list row: the row of string to be added
        """
        self.rows.append(row)

    def to_python(self):
        """Decode this Table object to standard Python types."""
        # Adding rows
        items = []
        for row in self.rows:
            formatted_row = [_format_python_value(v) for v in row]
            items.append(dict(zip(self.columns, formatted_row)))
        return items

    def prettytable(self):
        """Returns a new prettytable instance."""
        table = prettytable.PrettyTable(self.columns)
        if self.sortby:
            table.sortby = self.sortby
        for a_col, alignment in self.align.items():
            table.align[a_col] = alignment

        # Adding rows
        for row in self.rows:
            table.add_row(row)
        return table


class KeyValueTable(Table):
    """A table that is oriented towards key-value pairs."""
    def to_python(self):
        """Decode this KeyValueTable object to standard Python types."""
        mapping = {}
        for row in self.rows:
            mapping[row[0]] = _format_python_value(row[1])
        return mapping


class FormattedItem(object):
    """This is an object that can be displayed as a human readable and raw.

        :param original: raw (machine-readable) value
        :param string formatted: human-readable value
    """
    def __init__(self, original, formatted=None):
        self.original = original
        if formatted is not None:
            self.formatted = formatted
        else:
            self.formatted = self.original

    def to_python(self):
        """returns the original (raw) value."""
        return self.original

    def __str__(self):
        """returns the formatted value."""
        # If the original value is None, represent this as 'NULL'
        if self.original is None:
            return 'NULL'
        return str(self.original)

    __repr__ = __str__


def _format_python_value(value):
    """If the value has to_python() defined then return that."""
    if hasattr(value, 'to_python'):
        return value.to_python()
    return value
