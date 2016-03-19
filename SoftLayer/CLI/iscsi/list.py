"""List iSCSI targets."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils


@click.command()
@environment.pass_env
def cli(env):
    """List iSCSI targets."""

    iscsi_mgr = SoftLayer.ISCSIManager(env.client)
    iscsi_list = iscsi_mgr.list_iscsi()
    iscsi_list = [utils.NestedDict(n) for n in iscsi_list]
    table = formatting.Table([
        'id',
        'datacenter',
        'size',
        'username',
        'password',
        'server'
    ])
    for iscsi in iscsi_list:
        table.add_row([
            iscsi['id'],
            utils.lookup(iscsi,
                         'serviceResource',
                         'datacenter',
                         'name') or formatting.blank(),
            formatting.FormattedItem(iscsi.get('capacityGb',
                                               formatting.blank()),
                                     "%dGB" % iscsi.get('capacityGb', 0)),
            iscsi.get('username', formatting.blank()),
            iscsi.get('password', formatting.blank()),
            iscsi.get('serviceResourceBackendIpAddress',
                      formatting.blank())])

    env.fout(table)
