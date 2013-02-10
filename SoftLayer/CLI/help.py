#!/usr/bin/env python
"""Help"""
import sys

from SoftLayer.CLI import CLIRunnable


class Help(CLIRunnable):
    """ List active vlans with firewalls """
    action = None

    @classmethod
    def add_additional_args(cls, parser):
        cls.parser = parser

    @classmethod
    def execute(cls, client, args):
        cls.parser.print_help()
        sys.exit(1)
