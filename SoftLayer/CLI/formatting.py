"""
    SoftLayer.formatting
    ~~~~~~~~~~~~~~~~~~~~
    Provider classes and helper functions to display output onto a command-line.

"""
# pylint: disable=E0202, consider-merging-isinstance, arguments-differ, keyword-arg-before-vararg
import collections
import csv
import io
import json
import os
import sys

import click
from rich import box
from rich.errors import NotRenderableError
from rich.table import Table as rTable

from SoftLayer.CLI import exceptions
from SoftLayer import utils

FALSE_VALUES = ['0', 'false', 'FALSE', 'no', 'False']


def format_output(data, fmt='table', theme=None):  # pylint: disable=R0911,R0912
    """Given some data, will format it for console output.

    :param data: One of: String, Table, FormattedItem, List, Tuple, SequentialOutput
    :param string fmt (optional): One of: table, raw, json, python
    """
    if fmt == 'json':
        return json.dumps(data, indent=4, cls=CLIJSONEncoder)
    elif fmt == 'jsonraw':
        return json.dumps(data, cls=CLIJSONEncoder)
    if fmt == 'csv':
        return csv_output_format(data)

    if isinstance(data, str) or isinstance(data, rTable):
        return data

    # responds to .prettytable()
    if hasattr(data, 'prettytable') and fmt in ('table', 'raw'):
        return format_prettytable(data, fmt, theme)

    # responds to .to_python()
    if hasattr(data, 'to_python'):
        if fmt == 'json':
            return json.dumps(format_output(data, fmt='python'), indent=4, cls=CLIJSONEncoder)
        elif fmt == 'jsonraw':
            return json.dumps(format_output(data, fmt='python'), cls=CLIJSONEncoder)
        elif fmt == 'python':
            return data.to_python()

    # responds to .formatted
    if hasattr(data, 'formatted'):
        if fmt == 'table':
            return data.formatted

    # responds to .separator
    if hasattr(data, 'separator'):
        output = [format_output(d, fmt=fmt) for d in data if d]
        return str(SequentialOutput(data.separator, output))

    # is iterable
    if isinstance(data, list) or isinstance(data, tuple):
        output = [format_output(d, fmt=fmt) for d in data]
        if fmt == 'python':
            return output
        return output

    # fallback, convert this odd object to a string
    # print(f"Casting this to string {data}")
    return str(data)


def format_prettytable(table, fmt='table', theme=None):
    """Converts SoftLayer.CLI.formatting.Table instance to a prettytable."""
    for i, row in enumerate(table.rows):
        for j, item in enumerate(row):
            # Issue when adding items that evaulate to None (like empty lists) for Rich Tables
            # so we just cast those to a str
            if item:
                table.rows[i][j] = format_output(item)
            else:
                table.rows[i][j] = str(item)
    ptable = table.prettytable(fmt, theme)
    return ptable


def mb_to_gb(megabytes):
    """Converts number of megabytes to a FormattedItem in gigabytes.

    :param int megabytes: number of megabytes
    """
    return FormattedItem(megabytes, "%dG" % (float(megabytes) / 1024))


def b_to_gb(_bytes):
    """Converts number of bytes to a FormattedItem in gigabytes.

    :param int _bytes: number of bytes
    """
    return FormattedItem(_bytes, "%.2fG" % (float(_bytes) / 1024 / 1024 / 1024))


def gb(gigabytes):  # pylint: disable=C0103
    """Converts number of gigabytes to a FormattedItem in gigabytes.

    :param int gigabytes: number of gigabytes
    """
    return FormattedItem(int(float(gigabytes)) * 1024, "%dG" % int(float(gigabytes)))


def convert_sizes(value, unit='GB', round_result=False):
    """Converts a data storage value to an appropriate unit.

    :param str value: The value to convert.
    :param str unit: The unit of the value ('B', 'KB', 'MB', 'GB', 'TB').
    :param bool round_result: rounded result
    :return: The converted value and its unit.
    """

    if not value:
        return '0.00 MB'

    value = float(value)

    if value == 0:
        return "0.00 MB"

    units = ['B', 'KB', 'MB', 'GB', 'TB']
    if unit not in units:
        return "Invalid unit. Must be one of 'B', 'KB', 'MB', 'GB', 'TB'"

    unit_index = units.index(unit)

    while value > 999 and unit_index < len(units) - 1:
        value /= 1024
        unit_index += 1

    while value < 1 and unit_index > 0:
        value *= 1024
        unit_index -= 1

    if round_result:
        value = round(value / 5) * 5
    return f"{value:.2f} {units[unit_index]}"


def sum_sizes(size1, size2):
    """Sums two data storage values.

    :param str size1: The first value and its unit.
    :param str size2: The second value and its unit.
    :return: The sum of the values and its unit.
    """
    if size1 == '0.00 MB':
        return size2
    if size2 == '0.00 MB':
        return size1

    value1, unit1 = float(size1.split()[0]), size1.split()[1]
    value2, unit2 = float(size2.split()[0]), size2.split()[1]

    units = ['B', 'KB', 'MB', 'GB', 'TB']
    if unit1 not in units or unit2 not in units:
        return "Invalid unit in one of the sizes. Unit must be one of 'B', 'KB', 'MB', 'GB', 'TB'"

    value1 *= (1024 ** units.index(unit1))
    value2 *= (1024 ** units.index(unit2))

    total_value = value1 + value2

    total_unit = 'B'
    while total_value > 999 and total_unit != 'TB':
        total_value /= 1024
        total_unit = units[units.index(total_unit) + 1]

    return f"{total_value:.2f} {total_unit}"


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
    return transaction_status(utils.lookup(item, 'activeTransaction'))


def transaction_status(transaction):
    """Returns a FormattedItem describing the given transaction.

        :param item: An object capable of having an active transaction
    """
    if not transaction or not transaction.get('transactionStatus'):
        return blank()

    return FormattedItem(
        transaction['transactionStatus'].get('name'),
        transaction['transactionStatus'].get('friendlyName'))


def tags(tag_references):
    """Returns a formatted list of tags."""
    if not tag_references:
        return blank()

    tag_row = []
    for tag_detail in tag_references:
        tag = utils.lookup(tag_detail, 'tag', 'name')
        if tag is not None:
            tag_row.append(tag)

    return listing(tag_row, separator=', ')


def confirm(prompt_str, default=False):
    """Show a confirmation prompt to a command-line user.

    :param string prompt_str: prompt to give to the user
    :param bool default: Default value to True or False
    """
    if default:
        default_str = 'y'
        prompt = '%s [Y/n]' % prompt_str
    else:
        default_str = 'n'
        prompt = '%s [y/N]' % prompt_str

    ans = click.prompt(prompt, default=default_str, show_default=False)
    if ans.lower() in ('y', 'yes', 'yeah', 'yup', 'yolo'):
        return True

    return False


def no_going_back(confirmation):
    """Show a confirmation to a user.

    :param confirmation str: the string the user has to enter in order to
                             confirm their action.
    """
    if not confirmation:
        confirmation = 'yes'

    prompt = f"This action cannot be undone! Type '{confirmation}' or press Enter to abort"

    ans = click.prompt(prompt, default='', show_default=False)
    if ans.lower() == str(confirmation).lower():
        return True

    return False


class SequentialOutput(list):
    """SequentialOutput is used for outputting sequential items.

    The purpose is to de-couple the separator from the output itself.

    :param separator str: string to use as a default separator
    """

    def __init__(self, separator=os.linesep, *args, **kwargs):
        self.separator = separator
        super().__init__(*args, **kwargs)

    def to_python(self):
        """returns itself, since it itself is a list."""
        return self

    def __str__(self):
        return self.separator.join(str(x) for x in self)


class CLIJSONEncoder(json.JSONEncoder):
    """A JSON encoder which is able to use a .to_python() method on objects."""

    def default(self, o):
        """Encode object if it implements to_python()."""
        if hasattr(o, 'to_python'):
            return o.to_python()
        return super().default(o)


class Table(object):
    """A Table structure used for output.

    :param list columns: a list of column names
    """

    def __init__(self, columns, title=None, align=None):
        duplicated_cols = [col for col, count
                           in collections.Counter(columns).items()
                           if count > 1]
        if len(duplicated_cols) > 0:
            raise exceptions.CLIAbort("Duplicated columns are not allowed: %s"
                                      % ','.join(duplicated_cols))

        self.columns = columns
        self.rows = []
        self.align = align or {}
        self.sortby = None
        self.title = title
        # Used to print a message if the table is empty
        self.empty_message = None

    def __bool__(self):
        """Useful for seeing if the table has any rows"""
        return len(self.rows) > 0

    def set_empty_message(self, message):
        """Sets the empty message for this table for env.fout

        Set this message if you want to print a message instead of a table to the user
        but still want the json output to print an empty list `[]`

        :param message str: Message to print if the table has no rows
        """
        self.empty_message = message

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

    def prettytable(self, fmt='table', theme=None):
        """Returns a RICH table instance."""

        # Used to print a message instead of a bad looking empty table
        if not self and self.empty_message:
            return self.empty_message
        box_style = box.SQUARE
        if fmt == 'raw':
            box_style = None
        color_table = utils.table_color_theme(theme)
        table = rTable(title=self.title, box=box_style, header_style=color_table['header'])
        if self.sortby:
            try:
                # https://docs.python.org/3/howto/sorting.html#key-functions
                sort_index = self.columns.index(self.sortby)
                # All the values in `rows` are strings, so we need to cast to int for sorting purposes.
                self.rows.sort(key=lambda the_row: the_row[sort_index] if not the_row[sort_index].isdigit()
                               else int(the_row[sort_index]))
            except ValueError as ex:
                msg = "Column (%s) doesn't exist to sort by" % self.sortby
                raise exceptions.CLIAbort(msg) from ex

        for col in self.columns:
            justify = "center"
            style = None
            # This case aligns all columns in a table
            if isinstance(self.align, str):
                justify = self.align
            # This case alings a specific column
            elif isinstance(self.align, dict) and self.align.get(col, False):
                justify = self.align.get(col)
            # Backwards compatibility with PrettyTable style alignments
            if justify == 'r':
                justify = 'right'
            if justify == 'l':
                justify = 'left'
            # Special coloring for some columns
            if col in ('id', 'Id', 'ID'):
                style = color_table['id_columns']
            table.add_column(col, justify=justify, style=style)

        for row in self.rows:
            try:
                table.add_row(*row)
            # Generally you will see this if one of the columns in the row is a list or dict
            except NotRenderableError:
                forced_row = []
                for i in row:
                    forced_row.append(str(i))
                table.add_row(*forced_row)

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
            return "NULL"

        try:
            return str(self.original)
        except UnicodeError:
            return 'invalid'

    def __repr__(self):
        return 'FormattedItem(%r, %r)' % (self.original, self.formatted)

    # Implement sorting methods.
    # NOTE(kmcdonald): functools.total_ordering could be used once support for
    # Python 2.6 is dropped
    def __eq__(self, other):
        return self.original == getattr(other, 'original', other)

    def __lt__(self, other):
        if self.original is None:
            return True

        other_val = getattr(other, 'original', other)
        if other_val is None:
            return False
        return self.original < other_val

    def __gt__(self, other):
        return not (self < other or self == other)

    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return self >= other


def _format_python_value(value):
    """If the value has to_python() defined then return that."""
    if hasattr(value, 'to_python'):
        return value.to_python()
    return value


def iter_to_table(value):
    """Convert raw API responses to response tables."""
    if isinstance(value, list):
        return _format_list(value)
    if isinstance(value, dict):
        return _format_dict(value)
    return value


def _format_dict(result):
    """Format dictionary responses into key-value table."""

    table = KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'

    for key, value in result.items():
        value = iter_to_table(value)
        table.add_row([key, value])

    return table


def _format_list(result):
    """Format list responses into a table."""

    if not result:
        return result
    table = Table(['value'])
    new_result = [item for item in result if item]
    if len(new_result) == 0:
        table.add_row(["-"])
        return table
    if isinstance(new_result[0], dict):
        return _format_list_objects(new_result)

    for item in new_result:
        table.add_row([iter_to_table(item)])
    return table


def _format_list_objects(result):
    """Format list of objects into a table."""

    all_keys = set()
    for item in result:
        if isinstance(item, dict):
            all_keys = all_keys.union(item.keys())

    all_keys = sorted(all_keys)
    table = Table(all_keys)

    for item in result:
        if not item:
            continue
        values = []
        for key in all_keys:
            value = iter_to_table(item.get(key))
            values.append(value)

        table.add_row(values)

    return table


def csv_output_format(data, delimiter=','):
    """Formating a table to csv format and show it."""
    data = clean_table(data, delimiter)
    write_csv_format(sys.stdout, data, delimiter)
    return ''


def clean_table(data, delimiter):
    """Delete Null fields by '-' and fix nested table in table"""
    new_data_row = []
    for row in data.rows:
        new_value = []
        for value in row:
            if str(value) == 'NULL':
                value = '-'

            if str(type(value)) == "<class 'SoftLayer.CLI.formatting.Table'>":
                string_io = io.StringIO()
                write_csv_format(string_io, value, delimiter, quoting=csv.QUOTE_MINIMAL)

                nested_table_converted = string_io.getvalue()
                nested_table_converted = nested_table_converted.replace('\r', '').split('\n')
                nested_table_converted.pop()

                title_nested_table = new_value.pop()
                for item in nested_table_converted:
                    new_value.append(title_nested_table)
                    new_value.append(item)
                    new_data_row.append(new_value)
                    new_value = []
            else:
                new_value.append(value)

        if len(new_value) != 0:
            new_data_row.append(new_value)
    data.rows = new_data_row
    return data


def write_csv_format(support_output, data, delimiter, quoting=csv.QUOTE_NONNUMERIC):
    """Write csv format to supported output"""
    writer = csv.writer(support_output, delimiter=delimiter, quoting=quoting)
    writer.writerow(data.columns)
    writer.writerows(data.rows)
