"""
    SoftLayer.CLI.deprecated
    ~~~~~~~~~~~~~~~~~~~~~~~~
    Handles usage of the deprecated command name, 'sl'.
    :license: MIT, see LICENSE for more details.
"""
import sys

import click


@click.command()
def main():
    """Main function for the deprecated 'sl' command."""
    click.echo("ERROR: Use the 'slcli' command instead.", err=True)
    click.echo("> slcli %s" % ' '.join(sys.argv[1:]), err=True)
    exit(-1)
