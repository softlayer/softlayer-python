"""Search for SoftLayer Resources by simple phrase."""
# :license: MIT, see LICENSE for more details.


import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.search import SearchManager

object_types = {'ticket': 'SoftLayer_Ticket',
                'firewall': 'SoftLayer_Network_Vlan_Firewall',
                'vlan': 'SoftLayer_Network_Vlan',
                'subnet': 'SoftLayer_Network_Subnet_IpAddress',
                'delivery': 'SoftLayer_Network_Application_Delivery_Controller',
                'dedicated': 'SoftLayer_Virtual_DedicatedHost',
                'log': 'SoftLayer_Event_Log',
                'hardware': 'SoftLayer_Hardware',
                'virtual': 'SoftLayer_Virtual_Guest'}


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('query', nargs=-1)
@click.option('--types', is_flag=True, default=False, is_eager=True, help="Display searchable types.")
@click.option('--advanced', is_flag=True, help="Calls the AdvancedSearh API.")
@environment.pass_env
def cli(env, query, types, advanced):
    """Perform a query against the SoftLayer search database.

    Read More: https://sldn.softlayer.com/reference/services/SoftLayer_Search/search/
    Examples:

        slcli search test.com
        slcli search _objectType:SoftLayer_Virtual_Guest test.com
        slcli -vvv search _objectType:SoftLayer_Hardware hostname:testibm --advanced
    """
    search = SearchManager(env.client)
    # query is in array, so we need to convert it to a normal string for the API
    query = " ".join(query)
    if types:
        search_types = search.get_object_types()

        table = formatting.Table(["Name", "Properties"])
        table.align = "r"

        for type_object in search_types:
            prop_table = formatting.Table(["Property", "Sortable"])
            prop_table.align = "l"
            for prop in type_object.get('properties'):
                prop_table.add_row([prop.get('name'), prop.get('sortableFlag')])
            table.add_row([type_object.get('name'), prop_table])

        env.fout(table)
        return
    if advanced:
        result = search.advanced(query)

        env.fout(formatting.iter_to_table(result))
    else:
        result = search.search(query)
        env.fout(formatting.iter_to_table(result))
