"""Manage, delete, order compute instances."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer.CLI import template
from SoftLayer.CLI import virt
from SoftLayer import utils


def _update_with_like_args(ctx, _, value):
    """Update arguments with options taken from a currently running VS."""
    if value is None:
        return

    env = ctx.ensure_object(environment.Environment)
    vsi = SoftLayer.VSManager(env.client)
    vs_id = helpers.resolve_id(vsi.resolve_ids, value, 'VS')
    like_details = vsi.get_instance(vs_id)
    like_args = {
        'hostname': like_details['hostname'],
        'domain': like_details['domain'],
        'hourly': like_details['hourlyBillingFlag'],
        'datacenter': like_details['datacenter']['name'],
        'network': like_details['networkComponents'][0]['maxSpeed'],
        'userdata': like_details['userData'] or None,
        'postinstall': like_details.get('postInstallScriptUri'),
        'dedicated': like_details['dedicatedAccountHostOnlyFlag'],
        'private': like_details['privateNetworkOnlyFlag'],
    }

    like_args['flavor'] = utils.lookup(like_details,
                                       'billingItem',
                                       'orderItem',
                                       'preset',
                                       'keyName')
    if not like_args['flavor']:
        like_args['cpu'] = like_details['maxCpu']
        like_args['memory'] = '%smb' % like_details['maxMemory']

    tag_refs = like_details.get('tagReferences', None)
    if tag_refs is not None and len(tag_refs) > 0:
        like_args['tag'] = [t['tag']['name'] for t in tag_refs]

    # Handle mutually exclusive options
    like_image = utils.lookup(like_details,
                              'blockDeviceTemplateGroup',
                              'globalIdentifier')
    like_os = utils.lookup(like_details,
                           'operatingSystem',
                           'softwareLicense',
                           'softwareDescription',
                           'referenceCode')
    if like_image:
        like_args['image'] = like_image
    elif like_os:
        like_args['os'] = like_os

    if ctx.default_map is None:
        ctx.default_map = {}
    ctx.default_map.update(like_args)


def _parse_create_args(client, args):
    """Converts CLI arguments to args for VSManager.create_instance.

    :param dict args: CLI arguments
    """
    data = {
        "hourly": args.get('billing', 'hourly') == 'hourly',
        "domain": args['domain'],
        "hostname": args['hostname'],
        "private": args.get('private', None),
        "dedicated": args.get('dedicated', None),
        "disks": args['disk'],
        "cpus": args.get('cpu', None),
        "memory": args.get('memory', None),
        "flavor": args.get('flavor', None),
        "boot_mode": args.get('boot_mode', None)
    }

    # The primary disk is included in the flavor and the local_disk flag is not needed
    # Setting it to None prevents errors from the flag not matching the flavor
    if not args.get('san') and args.get('flavor'):
        data['local_disk'] = None
    else:
        data['local_disk'] = not args.get('san')

    if args.get('os'):
        data['os_code'] = args['os']

    if args.get('image'):
        if args.get('image').isdigit():
            image_mgr = SoftLayer.ImageManager(client)
            image_details = image_mgr.get_image(args.get('image'),
                                                mask="id,globalIdentifier")
            data['image_id'] = image_details['globalIdentifier']
        else:
            data['image_id'] = args['image']

    if args.get('datacenter'):
        data['datacenter'] = args['datacenter']

    if args.get('network'):
        data['nic_speed'] = args.get('network')

    if args.get('userdata'):
        data['userdata'] = args['userdata']
    elif args.get('userfile'):
        with open(args['userfile'], 'r') as userfile:
            data['userdata'] = userfile.read()

    if args.get('postinstall'):
        data['post_uri'] = args.get('postinstall')

    # Get the SSH keys
    if args.get('key'):
        keys = []
        for key in args.get('key'):
            resolver = SoftLayer.SshKeyManager(client).resolve_ids
            key_id = helpers.resolve_id(resolver, key, 'SshKey')
            keys.append(key_id)
        data['ssh_keys'] = keys

    if args.get('vlan_public'):
        data['public_vlan'] = args['vlan_public']

    if args.get('vlan_private'):
        data['private_vlan'] = args['vlan_private']

    data['public_subnet'] = args.get('subnet_public', None)

    data['private_subnet'] = args.get('subnet_private', None)

    if args.get('public_security_group'):
        pub_groups = args.get('public_security_group')
        data['public_security_groups'] = [group for group in pub_groups]

    if args.get('private_security_group'):
        priv_groups = args.get('private_security_group')
        data['private_security_groups'] = [group for group in priv_groups]

    if args.get('tag'):
        data['tags'] = ','.join(args['tag'])

    if args.get('host_id'):
        data['host_id'] = args['host_id']

    return data


@click.command(epilog="See 'slcli vs create-options' for valid options")
@click.option('--hostname', '-H',
              help="Host portion of the FQDN",
              required=True,
              prompt=True)
@click.option('--domain', '-D',
              help="Domain portion of the FQDN",
              required=True,
              prompt=True)
@click.option('--cpu', '-c',
              help="Number of CPU cores (not available with flavors)",
              type=click.INT)
@click.option('--memory', '-m',
              help="Memory in mebibytes (not available with flavors)",
              type=virt.MEM_TYPE)
@click.option('--flavor', '-f',
              help="Public Virtual Server flavor key name",
              type=click.STRING)
@click.option('--datacenter', '-d',
              help="Datacenter shortname",
              required=True,
              prompt=True)
@click.option('--os', '-o',
              help="OS install code. Tip: you can specify <OS>_LATEST")
@click.option('--image',
              help="Image ID. See: 'slcli image list' for reference")
@click.option('--boot-mode',
              help="Specify the mode to boot the OS in. Supported modes are HVM and PV.",
              type=click.STRING)
@click.option('--billing',
              type=click.Choice(['hourly', 'monthly']),
              default='hourly',
              show_default=True,
              help="Billing rate")
@click.option('--dedicated/--public',
              is_flag=True,
              help="Create a Dedicated Virtual Server")
@click.option('--host-id',
              type=click.INT,
              help="Host Id to provision a Dedicated Host Virtual Server onto")
@click.option('--san',
              is_flag=True,
              help="Use SAN storage instead of local disk.")
@click.option('--test',
              is_flag=True,
              help="Do not actually create the virtual server")
@click.option('--export',
              type=click.Path(writable=True, resolve_path=True),
              help="Exports options to a template file")
@click.option('--postinstall', '-i', help="Post-install script to download")
@helpers.multi_option('--key', '-k',
                      help="SSH keys to add to the root user")
@helpers.multi_option('--disk', help="Disk sizes")
@click.option('--private',
              is_flag=True,
              help="Forces the VS to only have access the private network")
@click.option('--like',
              is_eager=True,
              callback=_update_with_like_args,
              help="Use the configuration from an existing VS")
@click.option('--network', '-n', help="Network port speed in Mbps")
@helpers.multi_option('--tag', '-g', help="Tags to add to the instance")
@click.option('--template', '-t',
              is_eager=True,
              callback=template.TemplateCallback(list_args=['disk',
                                                            'key',
                                                            'tag']),
              help="A template file that defaults the command-line options",
              type=click.Path(exists=True, readable=True, resolve_path=True))
@click.option('--userdata', '-u', help="User defined metadata string")
@click.option('--userfile', '-F',
              help="Read userdata from file",
              type=click.Path(exists=True, readable=True, resolve_path=True))
@click.option('--vlan-public',
              help="The ID of the public VLAN on which you want the virtual "
                   "server placed",
              type=click.INT)
@click.option('--vlan-private',
              help="The ID of the private VLAN on which you want the virtual "
                   "server placed",
              type=click.INT)
@click.option('--subnet-public',
              help="The ID of the public SUBNET on which you want the virtual server placed",
              type=click.INT)
@click.option('--subnet-private',
              help="The ID of the private SUBNET on which you want the virtual server placed",
              type=click.INT)
@helpers.multi_option('--public-security-group',
                      '-S',
                      help=('Security group ID to associate with '
                            'the public interface'))
@helpers.multi_option('--private-security-group',
                      '-s',
                      help=('Security group ID to associate with '
                            'the private interface'))
@click.option('--wait',
              type=click.INT,
              help="Wait until VS is finished provisioning for up to X "
                   "seconds before returning")
@environment.pass_env
def cli(env, **args):
    """Order/create virtual servers."""
    vsi = SoftLayer.VSManager(env.client)
    _validate_args(env, args)

    # Do not create a virtual server with test or export
    do_create = not (args['export'] or args['test'])

    table = formatting.Table(['Item', 'cost'])
    table.align['Item'] = 'r'
    table.align['cost'] = 'r'
    data = _parse_create_args(env.client, args)

    output = []
    if args.get('test'):
        result = vsi.verify_create_instance(**data)

        if result['presetId']:
            ordering_mgr = SoftLayer.OrderingManager(env.client)
            item_prices = ordering_mgr.get_item_prices(result['packageId'])
            preset_prices = ordering_mgr.get_preset_prices(result['presetId'])
            search_keys = ["guest_core", "ram"]
            for price in preset_prices['prices']:
                if price['item']['itemCategory']['categoryCode'] in search_keys:
                    item_key_name = price['item']['keyName']
                    _add_item_prices(item_key_name, item_prices, result)

        table = _build_receipt_table(result['prices'], args.get('billing'))

        output.append(table)
        output.append(formatting.FormattedItem(
            None,
            ' -- ! Prices reflected here are retail and do not '
            'take account level discounts and are not guaranteed.'))

    if args['export']:
        export_file = args.pop('export')
        template.export_to_template(export_file, args,
                                    exclude=['wait', 'test'])
        env.fout('Successfully exported options to a template file.')

    if do_create:
        if not (env.skip_confirmations or formatting.confirm(
                "This action will incur charges on your account. Continue?")):
            raise exceptions.CLIAbort('Aborting virtual server order.')

        result = vsi.create_instance(**data)

        table = formatting.KeyValueTable(['name', 'value'])
        table.align['name'] = 'r'
        table.align['value'] = 'l'
        table.add_row(['id', result['id']])
        table.add_row(['created', result['createDate']])
        table.add_row(['guid', result['globalIdentifier']])
        output.append(table)

        if args.get('wait'):
            ready = vsi.wait_for_ready(result['id'], args.get('wait') or 1)
            table.add_row(['ready', ready])
            if ready is False:
                env.out(env.fmt(output))
                raise exceptions.CLIHalt(code=1)

    env.fout(output)


def _add_item_prices(item_key_name, item_prices, result):
    """Add the flavor item prices to the rest o the items prices"""
    for item in item_prices:
        if item_key_name == item['item']['keyName']:
            if 'pricingLocationGroup' in item:
                for location in item['pricingLocationGroup']['locations']:
                    if result['location'] == str(location['id']):
                        result['prices'].append(item)


def _build_receipt_table(prices, billing="hourly"):
    """Retrieve the total recurring fee of the items prices"""
    total = 0.000
    table = formatting.Table(['Cost', 'Item'])
    table.align['Cost'] = 'r'
    table.align['Item'] = 'l'
    for price in prices:
        rate = 0.000
        if billing == "hourly":
            rate += float(price.get('hourlyRecurringFee', 0.000))
        else:
            rate += float(price.get('recurringFee', 0.000))
        total += rate

        table.add_row(["%.3f" % rate, price['item']['description']])
    table.add_row(["%.3f" % total, "Total %s cost" % billing])
    return table


def _validate_args(env, args):
    """Raises an ArgumentError if the given arguments are not valid."""

    if all([args['cpu'], args['flavor']]):
        raise exceptions.ArgumentError(
            '[-c | --cpu] not allowed with [-f | --flavor]')

    if all([args['memory'], args['flavor']]):
        raise exceptions.ArgumentError(
            '[-m | --memory] not allowed with [-f | --flavor]')

    if all([args['dedicated'], args['flavor']]):
        raise exceptions.ArgumentError(
            '[-d | --dedicated] not allowed with [-f | --flavor]')

    if all([args['host_id'], args['flavor']]):
        raise exceptions.ArgumentError(
            '[-h | --host-id] not allowed with [-f | --flavor]')

    if all([args['userdata'], args['userfile']]):
        raise exceptions.ArgumentError(
            '[-u | --userdata] not allowed with [-F | --userfile]')

    image_args = [args['os'], args['image']]
    if all(image_args):
        raise exceptions.ArgumentError(
            '[-o | --os] not allowed with [--image]')

    while not any([args['os'], args['image']]):
        args['os'] = env.input("Operating System Code",
                               default="",
                               show_default=False)
        if not args['os']:
            args['image'] = env.input("Image", default="", show_default=False)
