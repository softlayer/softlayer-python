"""
    SoftLayer.CLI.deprecated
    ~~~~~~~~~~~~~~~~~~~~~~~~
    Handles usage of the deprecated command name, 'sl'.

    :license: MIT, see LICENSE for more details.
"""
import sys

import click


def main():
    """Main function for the deprecated 'sl' command."""
    click.echo("ERORR: Use the 'slcli' command instead.")
    click.echo("> slcli %s" % ' '.join(sys.argv[1:]))
    exit(-1)
