"""Lists subnets and their registration status."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.registration import ContactPerson
from SoftLayer import utils


@click.command()
@click.option('--sortby', help='Column to sort by',
              type=click.Choice(['id', 'identifier', 'type', 'network_space', 'datacenter',
                                 'vlan_id', 'IPs']))
@click.option('--datacenter', '-d', help="Filter by datacenter shortname (sng01, dal05, ...)")
@click.option('--subnet', help="Filter by subnet")
@click.option('--ipv4', '--v4', is_flag=True, help="Display only IPv4 subnets")
@click.option('--ipv6', '--v6', is_flag=True, help="Display only IPv6 subnets")
# TODO(CGALLO): Filter by Contact (might require post query filtering)
# TODO(CGALLO): Filter by Status, Show Complete / Unregistered / Maybe in progress if that is a thing
@environment.pass_env
def cli(env, sortby, datacenter, subnet, ipv4, ipv6):
    """Lists subnets and their registration status.

    Similar to the https://cloud.ibm.com/classic/network/rir page.
    """

    mgr = SoftLayer.NetworkManager(env.client)
    mask = """mask[id,networkIdentifier,cidr,subnetType,datacenter[name],note,
              registrations[status,personDetail[properties[propertyType]]],regionalInternetRegistry]"""

    table = formatting.Table(['Id', 'Subnet', 'Status', 'Datacenter', 'RIR', 'Contact', 'Subnet Notes'])
    table.sortby = sortby
    table.align = 'l'

    version = 0
    if ipv4:
        version = 4
    elif ipv6:
        version = 6

    subnets = mgr.list_subnets(
        datacenter=datacenter,
        version=version,
        identifier=subnet,
        network_space='PUBLIC',
        mask=mask
    )

    for subnet_record in subnets:
        # Get the last registration, which hopefully is the most current.
        subnet_registration = subnet_record.get('registrations')
        person = "None"
        status = "None"
        if subnet_registration:
            latest_registration = subnet_registration.pop()
            person = ContactPerson(latest_registration.get('personDetail'))
            status = utils.lookup(latest_registration, 'status', 'name')
            if status == "Registration Complete":
                status = "Complete"  # shorten it for readability.

        table.add_row([
            subnet_record['id'],
            "{}/{}".format(subnet_record['networkIdentifier'], str(subnet_record['cidr'])),
            status,
            utils.lookup(subnet_record, 'datacenter', 'name'),
            utils.lookup(subnet_record, 'regionalInternetRegistry', 'name'),
            str(person),
            formatting.trim(subnet_record.get('note'), 50)
        ])

    env.fout(table)
