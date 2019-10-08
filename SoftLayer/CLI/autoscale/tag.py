"""Tags all guests in an autoscale group."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.managers.autoscale import AutoScaleManager
from SoftLayer.managers.vs import VSManager


@click.command()
@click.argument('identifier')
@click.option('--tags', '-g', help="Tags to set for each guest in this group. Existing tags are overwritten. "
                                   "An empty string will remove all tags")
@environment.pass_env
def cli(env, identifier, tags):
    """Tags all guests in an autoscale group.

    --tags "Use, quotes, if you, want whitespace"

    --tags Otherwise,Just,commas
    """

    autoscale = AutoScaleManager(env.client)
    vsmanager = VSManager(env.client)
    mask = "mask[id,virtualGuestId,virtualGuest[tagReferences,id,hostname]]"
    guests = autoscale.get_virtual_guests(identifier, mask=mask)
    click.echo("New Tags: {}".format(tags))
    for guest in guests:
        real_guest = guest.get('virtualGuest')
        click.echo("Setting tags for {}".format(real_guest.get('hostname')))
        vsmanager.set_tags(tags, real_guest.get('id'),)
    click.echo("Done")
