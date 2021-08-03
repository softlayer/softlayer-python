"""Order and Cancel LBaaS instances."""
import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.exceptions import SoftLayerAPIError
from SoftLayer import utils


# pylint: disable=unused-argument
def parse_proto(ctx, param, value):
    """Parses the frontend and backend cli options"""
    proto = {'protocol': 'HTTP', 'port': 80}
    splitout = value.split(':')
    if len(splitout) != 2:
        raise exceptions.ArgumentError("{}={} is not properly formatted.".format(param, value))
    proto['protocol'] = splitout[0]
    proto['port'] = int(splitout[1])
    return proto


@click.command()
@click.option('--name', '-n', help='Label for this loadbalancer.', required=True)
@click.option('--datacenter', '-d', help='Datacenter shortname (dal13).', required=True)
@click.option('--label', '-l', help='A descriptive label for this loadbalancer.')
@click.option('--frontend', '-f', required=True, default='HTTP:80', show_default=True, callback=parse_proto,
              help='PROTOCOL:PORT string for incoming internet connections.')
@click.option('--backend', '-b', required=True, default='HTTP:80', show_default=True, callback=parse_proto,
              help='PROTOCOL:PORT string for connecting to backend servers.')
@click.option('--method', '-m', help="Balancing Method.", default='ROUNDROBIN', show_default=True,
              type=click.Choice(['ROUNDROBIN', 'LEASTCONNECTION', 'WEIGHTED_RR']))
@click.option('--subnet', '-s', required=True,
              help="Private subnet Id to order the LB on. See `slcli lb order-options`")
@click.option('--public', is_flag=True, default=False, show_default=True, help="Use a Public to Public loadbalancer.")
@click.option('--verify', is_flag=True, default=False, show_default=True,
              help="Only verify an order, dont actually create one.")
@environment.pass_env
def order(env, **args):
    """Creates a LB. Protocols supported are TCP, HTTP, and HTTPS."""

    mgr = SoftLayer.LoadBalancerManager(env.client)

    location = args.get('datacenter')
    name = args.get('name')
    description = args.get('label', None)

    backend = args.get('backend')
    frontend = args.get('frontend')
    protocols = [
        {
            "backendPort": backend.get('port'),
            "backendProtocol": backend.get('protocol'),
            "frontendPort": frontend.get('port'),
            "frontendProtocol": frontend.get('protocol'),
            "loadBalancingMethod": args.get('method'),
            "maxConn": 1000
        }
    ]

    # remove verify=True to place the order
    receipt = mgr.order_lbaas(location, name, description, protocols, args.get('subnet'),
                              public=args.get('public'), verify=args.get('verify'))
    table = parse_receipt(receipt)
    env.fout(table)


def parse_receipt(receipt):
    """Takes an order receipt and nicely formats it for cli output"""
    table = formatting.KeyValueTable(['Item', 'Cost'], title="Order: {}".format(receipt.get('orderId', 'Quote')))
    if receipt.get('prices'):
        for price in receipt.get('prices'):
            table.add_row([price['item']['description'], price['hourlyRecurringFee']])
    elif receipt.get('orderDetails'):
        for price in receipt['orderDetails']['prices']:
            table.add_row([price['item']['description'], price['hourlyRecurringFee']])

    return table


@click.command()
@click.option('--datacenter', '-d', help="Show only selected datacenter, use shortname (dal13) format.")
@environment.pass_env
def order_options(env, datacenter):
    """Prints options for order a LBaaS"""
    print("Prints options for ordering")
    mgr = SoftLayer.LoadBalancerManager(env.client)
    net_mgr = SoftLayer.NetworkManager(env.client)
    package = mgr.lbaas_order_options()

    if not datacenter:
        data_table = formatting.KeyValueTable(['Datacenters', 'City'])
        for region in package['regions']:
            data_table.add_row([region['description'].split('-')[0], region['description'].split('-')[1]])
            # print(region)
        env.fout(data_table)
        click.secho("Use `slcli lb order-options --datacenter <DC>` "
                    "to find pricing information and private subnets for that specific site.")

    else:
        for region in package['regions']:
            dc_name = utils.lookup(region, 'location', 'location', 'name')

            # Skip locations if they are not the one requested.
            if datacenter and dc_name != datacenter.lower():
                continue

            l_groups = []
            for group in region['location']['location']['groups']:
                l_groups.append(group.get('id'))

            # Price lookups
            prices = []
            price_table = formatting.KeyValueTable(['KeyName', 'Cost'], title='Prices')
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
            subnet_table = formatting.Table(['Id', 'Subnet', 'Vlan'], title='Private subnet')

            for subnet in subnets:
                # Only show these types, easier to filter here than in an API call.
                if subnet.get('subnetType') != 'PRIMARY' and \
                        subnet.get('subnetType') != 'ADDITIONAL_PRIMARY':
                    continue
                space = "{}/{}".format(subnet.get('networkIdentifier'), subnet.get('cidr'))
                vlan = "{}.{}".format(subnet['podName'], subnet['networkVlan']['vlanNumber'])
                subnet_table.add_row([subnet.get('id'), space, vlan])

            env.fout(price_table)
            env.fout(subnet_table)


@click.command()
@click.argument('identifier')
@environment.pass_env
def cancel(env, identifier):
    """Cancels a LBaaS instance"""

    mgr = SoftLayer.LoadBalancerManager(env.client)
    uuid, _ = mgr.get_lbaas_uuid_id(identifier)

    try:
        mgr.cancel_lbaas(uuid)
        click.secho("LB {} canceled succesfully.".format(identifier), fg='green')
    except SoftLayerAPIError as exception:
        click.secho("ERROR: {}".format(exception.faultString), fg='red')
