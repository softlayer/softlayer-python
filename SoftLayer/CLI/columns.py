"""
    SoftLayer.CLI.columns
    ~~~~~~~~~~~~~~~~~~~~~~
    Utilties for user-defined columns

    :license: MIT, see LICENSE for more details.
"""
import click

from SoftLayer import utils

# pylint: disable=unused-argument


class ColumnFormatter(object):
    """Maps each column using a function"""
    def __init__(self):
        self.columns = []
        self.column_funcs = []

    def add_column(self, name, func):
        """Add a new column along with a formatting function."""
        self.columns.append(name)
        self.column_funcs.append(func)

    def row(self, data):
        """Return a formatted row for the given data."""
        for column in self.column_funcs:
            if callable(column):
                yield column(data)
            else:
                yield utils.lookup(data, *column)


def get_formatter(column_map):
    """This function returns a callback to use with click options.

    The retuend function parses a comma-separated value and returns a new
    ColumnFormatter.

    :param column_map: a dictionary of the form: {col_name: function}.
    """

    def validate(ctx, param, value):
        """Click validation function."""
        try:
            formatter = ColumnFormatter()
            for column in [col.strip() for col in value.split(',')]:
                if column in column_map:
                    formatter.add_column(column, column_map[column])
                else:
                    formatter.add_column(column, (column,))

            return formatter
        except ValueError:
            raise click.BadParameter('rolls need to be in format NdM')

    return validate
