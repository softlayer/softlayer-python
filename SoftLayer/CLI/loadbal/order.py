"""Order and Cancel LBaaS instances."""
import click

import SoftLayer
from SoftLayer.CLI import environment, formatting, helpers, exceptions
from SoftLayer.exceptions import SoftLayerAPIError
from SoftLayer import utils
from pprint import pprint as pp 




@click.command()
@click.argument('identifier')
@environment.pass_env
def order(env, identifier):
    """Creates a LB"""
    print("Nothing yet")
    mgr = SoftLayer.LoadBalancerManager(env.client)
    package_name = 'Load Balancer As A Service (LBaaS)'
    location = 'MEXICO'
    name = 'My-LBaaS-name'
    description = 'A description sample'

    # Set False for private network
    is_public = True

    protocols = [        
        {
            "backendPort": 80,
            "backendProtocol": "HTTP",
            "frontendPort": 8080,
            "frontendProtocol": "HTTP",
            "loadBalancingMethod": "ROUNDROBIN",    # ROUNDROBIN, LEASTCONNECTION, WEIGHTED_RR
            "maxConn": 1000
        }
    ]

    # remove verify=True to place the order
    receipt = lbaas.order_lbaas(package_name, location, name, description,
                                protocols, public=is_public, verify=True)


@click.command()
@click.option('--datacenter', '-d', help="Show only selected datacenter, use shortname (dal13) format.")
@environment.pass_env
def order_options(env, datacenter):
    """Prints options for order a LBaaS"""
    print("Prints options for ordering")
    mgr = SoftLayer.LoadBalancerManager(env.client)
    net_mgr = SoftLayer.NetworkManager(env.client)
    package = mgr.lbaas_order_options()

    tables = []
    for region in package['regions']:
        dc_name = utils.lookup(region, 'location', 'location', 'name')

        # Skip locations if they are not the one requested.
        if datacenter and dc_name != datacenter:
            continue
        this_table = formatting.Table(
            ['Prices', 'Private Subnets'],
            title="{}: {}".format(region['keyname'], region['description'])
        )

        l_groups = []
        for group in region['location']['location']['groups']:
            l_groups.append(group.get('id'))

        # Price lookups
        prices = []
        price_table = formatting.KeyValueTable(['KeyName', 'Cost'])
        for item in package['items']:
            i_price = {'keyName': item['keyName']}
            for price in item.get('prices', []):
                if not price.get('locationGroupId'):
                    i_price['default_price'] = price.get('hourlyRecurringFee')
                elif price.get('locationGroupId') in l_groups:
                    i_price['region_price'] = price.get('hourlyRecurringFee')
            prices.append(i_price)
        for price in prices:
            if price.get('region_price'):
                price_table.add_row([price.get('keyName'), price.get('region_price')])
            else:
                price_table.add_row([price.get('keyName'), price.get('default_price')])

        # Vlan/Subnet Lookups
        mask = "mask[networkVlan,podName,addressSpace]"
        subnets = net_mgr.list_subnets(datacenter=dc_name, network_space='PRIVATE', mask=mask)
        subnet_table = formatting.KeyValueTable(['Subnet', 'Vlan'])

        for subnet in subnets:
            # Only show these types, easier to filter here than in an API call.
            if subnet.get('subnetType') != 'PRIMARY' and subnet.get('subnetType') != 'ADDITIONAL_PRIMARY':
                continue
            space = "{}/{}".format(subnet.get('networkIdentifier'), subnet.get('cidr'))
            vlan = "{}.{}".format(subnet['podName'], subnet['networkVlan']['vlanNumber'])
            subnet_table.add_row([space, vlan])
        this_table.add_row([price_table, subnet_table])

        env.fout(this_table)  


@click.command()
@environment.pass_env
def cancel(env, identifier,  **args):
    print("Nothing yet")