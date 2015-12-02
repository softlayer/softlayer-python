"""List NAS accounts."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils


@click.command()
@environment.pass_env
def cli(env):
    """List NAS accounts."""

    account = env.client['Account']

    nas_accounts = account.getNasNetworkStorage(
        mask='eventCount,serviceResource[datacenter.name]')

    table = formatting.Table(['id', 'datacenter', 'size', 'server'])

    for nas_account in nas_accounts:
        table.add_row([
            nas_account['id'],
            utils.lookup(nas_account,
                         'serviceResource',
                         'datacenter',
                         'name') or formatting.blank(),
            formatting.FormattedItem(
                nas_account.get('capacityGb', formatting.blank()),
                "%dGB" % nas_account.get('capacityGb', 0)),
            nas_account.get('serviceResourceBackendIpAddress',
                            formatting.blank())])

    env.fout(table)
