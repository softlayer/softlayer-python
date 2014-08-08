"""
    SoftLayer.CLI.helpers
    ~~~~~~~~~~~~~~~~~~~~~
    Helpers to be used in CLI modules in SoftLayer.CLI.modules.*

    :license: MIT, see LICENSE for more details.
"""

from SoftLayer.CLI import exceptions


def resolve_id(resolver, identifier, name='object'):
    """Resolves a single id using a resolver function.

    :param resolver: function that resolves ids. Should return None or a list
                     of ids.
    :param string identifier: a string identifier used to resolve ids
    :param string name: the object type, to be used in error messages

    """
    ids = resolver(identifier)

    if len(ids) == 0:
        raise exceptions.CLIAbort("Error: Unable to find %s '%s'"
                                  % (name, identifier))

    if len(ids) > 1:
        raise exceptions.CLIAbort(
            "Error: Multiple %s found for '%s': %s" %
            (name, identifier, ', '.join([str(_id) for _id in ids])))

    return ids[0]


def sanitize_args(args):
    """ sanitize input (remove = sign from argument values)
    :returns args back
    """
    for key, value in args.items():
        if isinstance(value, str) and value.startswith('='):
            args[key] = value[1:]
    return args
