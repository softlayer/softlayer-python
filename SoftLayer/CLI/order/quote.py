"""View and Order a quote"""
# :license: MIT, see LICENSE for more details.
import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer.managers import ImageManager as ImageManager
from SoftLayer.managers import ordering
from SoftLayer.managers import SshKeyManager as SshKeyManager


def _parse_create_args(client, args):
    """Converts CLI arguments to args for VSManager.create_instance.

    :param dict args: CLI arguments
    """
    data = {}

    if args.get('quantity'):
        data['quantity'] = int(args.get('quantity'))
    if args.get('postinstall'):
        data['provisionScripts'] = [args.get('postinstall')]
    if args.get('complex_type'):
        data['complexType'] = args.get('complex_type')

    if args.get('fqdn'):
        servers = []
        for name in args.get('fqdn'):
            fqdn = name.split(".", 1)
            servers.append({'hostname': fqdn[0], 'domain': fqdn[1]})
        data['hardware'] = servers

    if args.get('image'):
        if args.get('image').isdigit():
            image_mgr = ImageManager(client)
            image_details = image_mgr.get_image(args.get('image'), mask="id,globalIdentifier")
            data['imageTemplateGlobalIdentifier'] = image_details['globalIdentifier']
        else:
            data['imageTemplateGlobalIdentifier'] = args['image']

    userdata = None
    if args.get('userdata'):
        userdata = args['userdata']
    elif args.get('userfile'):
        with open(args['userfile'], 'r') as userfile:
            userdata = userfile.read()
    if userdata:
        for hardware in data['hardware']:
            hardware['userData'] = [{'value': userdata}]

    # Get the SSH keys
    if args.get('key'):
        keys = []
        for key in args.get('key'):
            resolver = SshKeyManager(client).resolve_ids
            key_id = helpers.resolve_id(resolver, key, 'SshKey')
            keys.append(key_id)
        data['sshKeys'] = keys

    return data


@click.command()
@click.argument('quote')
@click.option('--verify', is_flag=True, default=False, show_default=True,
              help="If specified, will only show what the quote will order, will NOT place an order")
@click.option('--quantity', type=int, default=None,
              help="The quantity of the item being ordered if different from quoted value")
@click.option('--complex-type', default='SoftLayer_Container_Product_Order_Hardware_Server', show_default=True,
              help=("The complex type of the order. Starts with 'SoftLayer_Container_Product_Order'."))
@click.option('--userdata', '-u', help="User defined metadata string")
@click.option('--userfile', '-F', type=click.Path(exists=True, readable=True, resolve_path=True),
              help="Read userdata from file")
@click.option('--postinstall', '-i', help="Post-install script to download")
@helpers.multi_option('--key', '-k', help="SSH keys to add to the root user")
@helpers.multi_option('--fqdn', required=True,
                      help="<hostname>.<domain.name.tld> formatted name to use. Specify one fqdn per server")
@click.option('--image', help="Image ID. See: 'slcli image list' for reference")
@environment.pass_env
def cli(env, quote, **args):
    """View and Order a quote

    \f
    :note:
        The hostname and domain are split out from the fully qualified domain name.

        If you want to order multiple servers, you need to specify each FQDN. Postinstall, userdata, and
        sshkeys are applied to all servers in an order.

    ::

        slcli order quote 12345 --fqdn testing.tester.com \\
            --complex-type SoftLayer_Container_Product_Order_Virtual_Guest -k sshKeyNameLabel\\
            -i https://domain.com/runthis.sh --userdata DataGoesHere

    """
    table = formatting.Table([
        'Id', 'Name', 'Created', 'Expiration', 'Status'
    ])
    create_args = _parse_create_args(env.client, args)

    manager = ordering.OrderingManager(env.client)
    quote_details = manager.get_quote_details(quote)

    package = quote_details['order']['items'][0]['package']
    create_args['packageId'] = package['id']

    if args.get('verify'):
        result = manager.verify_quote(quote, create_args)
        verify_table = formatting.Table(['keyName', 'description', 'cost'])
        verify_table.align['keyName'] = 'l'
        verify_table.align['description'] = 'l'
        for price in result['prices']:
            cost_key = 'hourlyRecurringFee' if result['useHourlyPricing'] is True else 'recurringFee'
            verify_table.add_row([
                price['item']['keyName'],
                price['item']['description'],
                price[cost_key] if cost_key in price else formatting.blank()
            ])
        env.fout(verify_table)
    else:
        result = manager.order_quote(quote, create_args)
        table = formatting.KeyValueTable(['name', 'value'])
        table.align['name'] = 'r'
        table.align['value'] = 'l'
        table.add_row(['id', result['orderId']])
        table.add_row(['created', result['orderDate']])
        table.add_row(['status', result['placedOrder']['status']])
        env.fout(table)
