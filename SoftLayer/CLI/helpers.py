"""
    SoftLayer.CLI.helpers
    ~~~~~~~~~~~~~~~~~~~~~
    Helpers to be used in CLI modules in SoftLayer.CLI.modules.*

    :license: MIT, see LICENSE for more details.
"""

import click

from SoftLayer.CLI import exceptions


def multi_option(*param_decls, **attrs):
    """modify help text and indicate option is permitted multiple times

    :param param_decls:
    :param attrs:
    :return:

    """
    attrhelp = attrs.get('help', None)
    if attrhelp is not None:
        newhelp = attrhelp + " (multiple occurrence permitted)"
        attrs['help'] = newhelp
    attrs['multiple'] = True
    return click.option(*param_decls, **attrs)


def resolve_id(resolver, identifier, name='object'):
    """Resolves a single id using a resolver function.

    :param resolver: function that resolves ids. Should return None or a list of ids.
    :param string identifier: a string identifier used to resolve ids
    :param string name: the object type, to be used in error messages

    """
    try:
        return int(identifier)
    except ValueError:
        pass  # It was worth a shot

    ids = resolver(identifier)

    if len(ids) == 0:
        raise exceptions.CLIAbort("Error: Unable to find %s '%s'" % (name, identifier))

    if len(ids) > 1:
        raise exceptions.CLIAbort(
            "Error: Multiple %s found for '%s': %s" %
            (name, identifier, ', '.join([str(_id) for _id in ids])))

    return ids[0]
