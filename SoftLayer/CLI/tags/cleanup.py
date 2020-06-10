"""Removes unused Tags"""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.managers.tags import TagManager


@click.command()
@click.option('--dry-run', '-d', is_flag=True, default=False,
              help="Don't delete, just show what will be deleted.")
@environment.pass_env
def cli(env, dry_run):
    """Removes all empty tags."""

    tag_manager = TagManager(env.client)
    empty_tags = tag_manager.get_unattached_tags()

    for tag in empty_tags:
        if dry_run:
            click.secho("(Dry Run) Removing {}".format(tag.get('name')), fg='yellow')
        else:
            result = tag_manager.delete_tag(tag.get('name'))
            color = 'green' if result else 'red'
            click.secho("Removing {}".format(tag.get('name')), fg=color)
