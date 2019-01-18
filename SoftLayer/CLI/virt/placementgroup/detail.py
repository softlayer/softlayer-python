"""View details of a placement group"""

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer.managers.vs_placement import PlacementManager as PlacementManager


@click.command(epilog="Once provisioned, virtual guests can be managed with the slcli vs commands")
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """View details of a placement group.

    IDENTIFIER can be either the Name or Id of the placement group you want to view
    """
    manager = PlacementManager(env.client)
    group_id = helpers.resolve_id(manager.resolve_ids, identifier, 'placement_group')
    result = manager.get_object(group_id)
    table = formatting.Table(["Id", "Name", "Backend Router", "Rule", "Created"])

    table.add_row([
        result['id'],
        result['name'],
        result['backendRouter']['hostname'],
        result['rule']['name'],
        result['createDate']
    ])
    guest_table = formatting.Table([
        "Id",
        "FQDN",
        "Primary IP",
        "Backend IP",
        "CPU",
        "Memory",
        "Provisioned",
        "Transaction"
    ])
    for guest in result['guests']:
        guest_table.add_row([
            guest.get('id'),
            guest.get('fullyQualifiedDomainName'),
            guest.get('primaryIpAddress'),
            guest.get('primaryBackendIpAddress'),
            guest.get('maxCpu'),
            guest.get('maxMemory'),
            guest.get('provisionDate'),
            formatting.active_txn(guest)
        ])

    env.fout(table)
    env.fout(guest_table)
