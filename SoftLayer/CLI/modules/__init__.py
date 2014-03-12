"""
    SoftLayer.CLI.modules
    ~~~~~~~~~~~~~~~~~~~~~
    Contains all plugable modules for the CLI interface

    :license: MIT, see LICENSE for more details.
"""

from pkgutil import iter_modules


def get_module_list():
    """ Returns each module under SoftLayer.CLI.modules """
    actions = [action[1] for action in iter_modules(__path__)]
    return actions
