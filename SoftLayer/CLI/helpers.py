"""
    SoftLayer.CLI.helpers
    ~~~~~~~~~~~~~~~~~~~~~
    Helpers to be used in CLI modules in SoftLayer.CLI.modules.*

    :license: MIT, see LICENSE for more details.
"""

from SoftLayer.utils import NestedDict
from SoftLayer.CLI.environment import CLIRunnable
from .exceptions import CLIHalt, CLIAbort, ArgumentError
from .formatting import (
    Table, KeyValueTable, FormattedItem, SequentialOutput, confirm,
    no_going_back, mb_to_gb, gb, listing, blank, format_output,
    active_txn, valid_response, transaction_status)
from .template import update_with_template_args, export_to_template

__all__ = [
    # Core/Misc
    'CLIRunnable', 'NestedDict', 'FALSE_VALUES', 'resolve_id',
    # Exceptions
    'CLIAbort', 'CLIHalt', 'ArgumentError',
    # Formatting
    'Table', 'KeyValueTable', 'FormattedItem', 'SequentialOutput',
    'valid_response', 'confirm', 'no_going_back', 'mb_to_gb', 'gb',
    'listing', 'format_output', 'blank', 'active_txn', 'transaction_status',
    # Template
    'update_with_template_args', 'export_to_template',
]

FALSE_VALUES = ['0', 'false', 'FALSE', 'no', 'False']


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
