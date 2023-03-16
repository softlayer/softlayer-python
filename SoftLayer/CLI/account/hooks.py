"""Show all Provisioning Scripts."""
# :license: MIT, see LICENSE for more details.
import click


from SoftLayer.CLI.command import SLCommand as SLCommand
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers import account


@click.command(cls=SLCommand)
@environment.pass_env
def cli(env):
    """Show all Provisioning Scripts."""

    manager = account.AccountManager(env.client)
    hooks = manager.get_provisioning_scripts()

    table = formatting.Table(["Id", "Name", "Uri"])

    for hook in hooks:
        table.add_row([hook.get('id'), hook.get('name'), hook.get('uri')])

    env.fout(table)
