"""Order/create a VLAN instance."""
# :license: MIT, see LICENSE for more details.
import click
import SoftLayer
from SoftLayer.managers import ordering

from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting


@click.command()
@click.option('--name', required=False, prompt=True, help="Vlan name")
@click.option('--datacenter', '-d', required=False, help="Datacenter shortname")
@click.option('--pod', '-p', required=False, help="Pod name. E.g dal05.pod01")
@click.option('--network', default='public', show_default=True, type=click.Choice(['public', 'private']),
              help='Network vlan type')
@click.option('--billing', default='hourly', show_default=True, type=click.Choice(['hourly', 'monthly']),
              help="Billing rate")
@environment.pass_env
def cli(env, name, datacenter, pod, network, billing):
    """Order/create a VLAN instance."""

    item_package = ['PUBLIC_NETWORK_VLAN']
    complex_type = 'SoftLayer_Container_Product_Order_Network_Vlan'
    extras = {'name': name}
    if pod:
        datacenter = pod.split('.')[0]
        mgr = SoftLayer.NetworkManager(env.client)
        pods = mgr.get_pods()
        for router in pods:
            if router.get('name') == pod:
                if network == 'public':
                    extras['routerId'] = router.get('frontendRouterId')
                elif network == 'private':
                    extras['routerId'] = router.get('backendRouterId')
                break
        if not extras.get('routerId'):
            raise exceptions.CLIAbort(
                "Unable to find pod name: {}".format(pod))
    if network == 'private':
        item_package = ['PRIVATE_NETWORK_VLAN']

    ordering_manager = ordering.OrderingManager(env.client)
    result = ordering_manager.place_order(package_keyname='NETWORK_VLAN',
                                          location=datacenter,
                                          item_keynames=item_package,
                                          complex_type=complex_type,
                                          hourly=billing,
                                          extras=extras)
    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'
    table.add_row(['id', result['orderId']])
    table.add_row(['created', result['orderDate']])
    table.add_row(['name', result['orderDetails']['orderContainers'][0]['name']])

    env.fout(table)
