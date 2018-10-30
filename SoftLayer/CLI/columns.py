"""
    SoftLayer.CLI.columns
    ~~~~~~~~~~~~~~~~~~~~~~
    Utilties for user-defined columns

    :license: MIT, see LICENSE for more details.
"""
import click

from SoftLayer import utils

# pylint: disable=unused-argument


class Column(object):
    """Column desctribes an attribute and how to fetch/display it."""

    def __init__(self, name, path, mask=None):
        self.name = name
        self.path = path
        self.mask = mask

        # If the mask is not set explicitly, infer it from the path
        if self.mask is None and isinstance(path, (tuple, list)):
            self.mask = '.'.join(path)


class ColumnFormatter(object):
    """Maps each column using a function"""

    def __init__(self):
        self.columns = []
        self.column_funcs = []
        self.mask_parts = set()

    def add_column(self, column):
        """Add a new column along with a formatting function."""
        self.columns.append(column.name)
        self.column_funcs.append(column.path)

        if column.mask is not None:
            self.mask_parts.add(column.mask)

    def row(self, data):
        """Return a formatted row for the given data."""
        for column in self.column_funcs:
            if callable(column):
                yield column(data)
            else:
                yield utils.lookup(data, *column)

    def mask(self):
        """Returns a SoftLayer mask to fetch data needed for each column."""
        return ','.join(self.mask_parts)


def get_formatter(columns):
    """This function returns a callback to use with click options.

    The returned function parses a comma-separated value and returns a new
    ColumnFormatter.

    :param columns: a list of Column instances
    """

    column_map = dict((column.name, column) for column in columns)

    def validate(ctx, param, value):
        """Click validation function."""
        if value == '':
            raise click.BadParameter('At least one column is required.')

        formatter = ColumnFormatter()
        for column in [col.strip() for col in value.split(',')]:
            if column in column_map:
                formatter.add_column(column_map[column])
            else:
                formatter.add_column(Column(column, column.split('.')))

        return formatter

    return validate
