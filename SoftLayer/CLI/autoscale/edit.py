"""Edits an Autoscale group."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.managers.autoscale import AutoScaleManager


@click.command()
@click.argument('identifier')
@click.option('--name', help="Scale group's name.")
@click.option('--min', 'minimum', type=click.INT, help="Set the minimum number of guests")
@click.option('--max', 'maximum', type=click.INT, help="Set the maximum number of guests")
@click.option('--userdata', help="User defined metadata string")
@click.option('--userfile', '-F', help="Read userdata from a file",
              type=click.Path(exists=True, readable=True, resolve_path=True))
@click.option('--cpu', type=click.INT, help="Number of CPUs for new guests (existing not effected")
@click.option('--memory', type=click.INT, help="RAM in MB or GB for new guests (existing not effected")
@environment.pass_env
def cli(env, identifier, name, minimum, maximum, userdata, userfile, cpu, memory):
    """Edits an Autoscale group."""

    template = {}
    autoscale = AutoScaleManager(env.client)
    group = autoscale.details(identifier)

    template['name'] = name
    template['minimumMemberCount'] = minimum
    template['maximumMemberCount'] = maximum
    virt_template = {}
    if userdata:
        virt_template['userData'] = [{"value": userdata}]
    elif userfile:
        with open(userfile, 'r', encoding="utf-8") as userfile_obj:
            virt_template['userData'] = [{"value": userfile_obj.read()}]
    virt_template['startCpus'] = cpu
    virt_template['maxMemory'] = memory

    # Remove any entries that are `None` as the API will complain about them.
    template['virtualGuestMemberTemplate'] = clean_dict(virt_template)
    clean_template = clean_dict(template)

    # If there are any values edited in the template, we need to get the OLD template values and replace them.
    if template['virtualGuestMemberTemplate']:
        # Update old template with new values
        for key, value in clean_template['virtualGuestMemberTemplate'].items():
            group['virtualGuestMemberTemplate'][key] = value
        clean_template['virtualGuestMemberTemplate'] = group['virtualGuestMemberTemplate']

    autoscale.edit(identifier, clean_template)
    click.echo("Done")


def clean_dict(dictionary):
    """Removes any `None` entires from the dictionary"""
    return {k: v for k, v in dictionary.items() if v}
