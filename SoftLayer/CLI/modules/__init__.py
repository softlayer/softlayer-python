"""
    SoftLayer.CLI.modules
    ~~~~~~~~~~~~~~~~~~~~~
    Contains all plugable modules for the CLI interface

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: MIT, see LICENSE for more details.
"""

from pkgutil import iter_modules


def get_module_list():
    actions = [action[1] for action in iter_modules(__path__)]
    return actions
