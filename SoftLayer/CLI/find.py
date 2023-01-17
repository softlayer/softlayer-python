"""Search for SoftLayer Resources by simple phrase."""
# :license: MIT, see LICENSE for more details.


import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers.search import SearchingManager

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
@click.argument('query')
@click.option('--types',
              is_flag=True, default=False,
              help="Show only planned events")
@click.option('--advanced', is_flag=True, help="Show only planned events")
@environment.pass_env
def cli(env, query, types, advanced):
    searching = SearchingManager(env.client)
    name = object_types.get(query)
    if types:
        object_type = searching.get_object_types()

        table = formatting.Table(["Name", "Type", 'Resource'])

        for type_object in object_type:
            for property in type_object['properties']:
                if name == type_object['name']:
                    table.add_row([property['name'], property['type'], type_object['name']])

        env.fout(table)
    if advanced:
        search_string = '_objectType:' + name
        result = searching.advanced(search_string)

        env.fout(formatting.iter_to_table(result))
