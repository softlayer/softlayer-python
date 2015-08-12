"""
    SoftLayer.CLI.deprecated
    ~~~~~~~~~~~~~~~~~~~~~~~~
    Handles usage of the deprecated command name, 'sl'.
    :license: MIT, see LICENSE for more details.
"""
from __future__ import print_function
import sys


def main():
    """Main function for the deprecated 'sl' command."""
    print("ERROR: Use the 'slcli' command instead.", file=sys.stderr)
    print("> slcli %s" % ' '.join(sys.argv[1:]), file=sys.stderr)
    exit(-1)
