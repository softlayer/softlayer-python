#!/usr/bin/env python
"""Lists all available commands"""
from SoftLayer.CLI import action_list, load_module, Table


def execute(args):
    actions = action_list()
    t = Table([
        "module",
        "description",
    ])
    t.align['module'] = 'r'
    t.align['description'] = 'l'

    for action in actions:
        m = load_module(action)
        t.add_row([action, m.__doc__])

    return t
