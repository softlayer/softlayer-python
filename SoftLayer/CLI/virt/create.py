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
        'placement_id': like_details.get('placementGroupId', None),
        'transient': like_details.get('transientGuestFlag', None),
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
        "cpus": args.get('cpu', None),
        "ipv6": args.get('ipv6', None),
        "disks": args.get('disk', None),
        "os_code": args.get('os', None),
        "memory": args.get('memory', None),
        "flavor": args.get('flavor', None),
        "domain": args.get('domain', None),
        "host_id": args.get('host_id', None),
        "private": args.get('private', None),
        "transient": args.get('transient', None),
        "hostname": args.get('hostname', None),
        "nic_speed": args.get('network', None),
        "boot_mode": args.get('boot_mode', None),
        "dedicated": args.get('dedicated', None),
        "post_uri": args.get('postinstall', None),
        "datacenter": args.get('datacenter', None),
        "public_vlan": args.get('vlan_public', None),
        "private_vlan": args.get('vlan_private', None),
        "public_subnet": args.get('subnet_public', None),
        "private_subnet": args.get('subnet_private', None),
        "public_router": args.get('router_public', None),
        "private_router": args.get('router_private', None),
    }

    # The primary disk is included in the flavor and the local_disk flag is not needed
    # Setting it to None prevents errors from the flag not matching the flavor
    if not args.get('san') and args.get('flavor'):
        data['local_disk'] = None
    else:
        data['local_disk'] = not args.get('san')

    if args.get('image'):
        if args.get('image').isdigit():
            image_mgr = SoftLayer.ImageManager(client)
            image_details = image_mgr.get_image(args.get('image'),
                                                mask="id,globalIdentifier")
            data['image_id'] = image_details['globalIdentifier']
        else:
            data['image_id'] = args['image']

    if args.get('userdata'):
        data['userdata'] = args['userdata']
    elif args.get('userfile'):
        with open(args['userfile'], 'r', encoding="utf-8") as userfile:
            data['userdata'] = userfile.read()

    # Get the SSH keys
    if args.get('key'):
        keys = []
        for key in args.get('key'):
            resolver = SoftLayer.SshKeyManager(client).resolve_ids
            key_id = helpers.resolve_id(resolver, key, 'SshKey')
            keys.append(key_id)
        data['ssh_keys'] = keys

    if args.get('public_security_group'):
        pub_groups = args.get('public_security_group')
        data['public_security_groups'] = list(pub_groups)

    if args.get('private_security_group'):
        priv_groups = args.get('private_security_group')
        data['private_security_groups'] = list(priv_groups)

    if args.get('tag', False):
        data['tags'] = ','.join(args['tag'])

    if args.get('host_id'):
        data['host_id'] = args['host_id']

    if args.get('placementgroup'):
        resolver = SoftLayer.managers.PlacementManager(client).resolve_ids
        data['placement_id'] = helpers.resolve_id(resolver, args.get('placementgroup'), 'PlacementGroup')

    return data


@click.command(epilog="See 'slcli vs create-options' for valid options")
@click.option('--hostname', '-H', required=True, prompt=True, help="Host portion of the FQDN")
@click.option('--domain', '-D', required=True, prompt=True, help="Domain portion of the FQDN")
@click.option('--cpu', '-c', type=click.INT, help="Number of CPU cores (not available with flavors)")
@click.option('--memory', '-m', type=virt.MEM_TYPE, help="Memory in mebibytes (not available with flavors)")
@click.option('--flavor', '-f', type=click.STRING, help="Public Virtual Server flavor key name")
@click.option('--datacenter', '-d', required=True, prompt=True, help="Datacenter shortname")
@click.option('--os', '-o', help="OS install code. Tip: you can specify <OS>_LATEST")
@click.option('--image', help="Image ID. See: 'slcli image list' for reference")
@click.option('--boot-mode', type=click.STRING,
              help="Specify the mode to boot the OS in. Supported modes are HVM and PV.")
@click.option('--billing', type=click.Choice(['hourly', 'monthly']), default='hourly', show_default=True,
              help="Billing rate")
@click.option('--dedicated/--public', is_flag=True, help="Create a Dedicated Virtual Server")
@click.option('--host-id', type=click.INT, help="Host Id to provision a Dedicated Host Virtual Server onto")
@click.option('--san', is_flag=True, help="Use SAN storage instead of local disk.")
@click.option('--test', is_flag=True, help="Do not actually create the virtual server")
@click.option('--export', type=click.Path(writable=True, resolve_path=True),
              help="Exports options to a template file")
@click.option('--postinstall', '-i', help="Post-install script to download")
@helpers.multi_option('--key', '-k', help="SSH keys to add to the root user")
@helpers.multi_option('--disk', help="Disk sizes")
@click.option('--private', is_flag=True,
              help="Forces the VS to only have access the private network")
@click.option('--like', is_eager=True, callback=_update_with_like_args,
              help="Use the configuration from an existing VS")
@click.option('--network', '-n', help="Network port speed in Mbps", type=click.INT)
@helpers.multi_option('--tag', '-g', help="Tags to add to the instance")
@click.option('--template', '-t', is_eager=True,
              callback=template.TemplateCallback(list_args=['disk', 'key', 'tag']),
              help="A template file that defaults the command-line options",
              type=click.Path(exists=True, readable=True, resolve_path=True))
@click.option('--userdata', '-u', help="User defined metadata string")
@click.option('--userfile', '-F', type=click.Path(exists=True, readable=True, resolve_path=True),
              help="Read userdata from file")
@click.option('--vlan-public', type=click.INT,
              help="The ID of the public VLAN on which you want the virtual server placed")
@click.option('--vlan-private', type=click.INT,
              help="The ID of the private VLAN on which you want the virtual server placed")
@click.option('--subnet-public', type=click.INT,
              help="The ID of the public SUBNET on which you want the virtual server placed")
@click.option('--subnet-private', type=click.INT,
              help="The ID of the private SUBNET on which you want the virtual server placed")
@click.option('--router-public', type=click.INT,
              help="The ID of the public ROUTER on which you want the virtual server placed")
@click.option('--router-private', type=click.INT,
              help="The ID of the private ROUTER on which you want the virtual server placed")
@helpers.multi_option('--public-security-group', '-S',
                      help=('Security group ID to associate with the public interface'))
@helpers.multi_option('--private-security-group', '-s',
                      help=('Security group ID to associate with the private interface'))
@click.option('--wait', type=click.INT,
              help="Wait until VS is finished provisioning for up to X seconds before returning")
@click.option('--placementgroup',
              help="Placement Group name or Id to order this guest on. See: slcli vs placementgroup list")
@click.option('--ipv6', is_flag=True, help="Adds an IPv6 address to this guest")
@click.option('--transient', is_flag=True,
              help="Create a transient virtual server")
@environment.pass_env
def cli(env, **args):
    """Order/create virtual servers."""

    vsi = SoftLayer.VSManager(env.client)
    _validate_args(env, args)
    create_args = _parse_create_args(env.client, args)
    test = args.get('test', False)
    do_create = not (args.get('export') or test)

    if do_create:
        if not (env.skip_confirmations or formatting.confirm(
                "This action will incur charges on your account. Continue?")):
            raise exceptions.CLIAbort('Aborting virtual server order.')

    if args.get('export'):
        export_file = args.pop('export')
        template.export_to_template(export_file, args, exclude=['wait', 'test'])
        env.fout('Successfully exported options to a template file.')

    else:
        result = vsi.order_guest(create_args, test)
        output = _build_receipt_table(result, args.get('billing'), test)

        if do_create:
            env.fout(_build_guest_table(result))
        env.fout(output)

        if args.get('wait'):
            virtual_guests = utils.lookup(result, 'orderDetails', 'virtualGuests')
            guest_id = virtual_guests[0]['id']
            click.secho("Waiting for %s to finish provisioning..." % guest_id, fg='green')
            ready = vsi.wait_for_ready(guest_id, args.get('wait') or 1)
            if ready is False:
                env.out(env.fmt(output))
                raise exceptions.CLIHalt(code=1)


def _build_receipt_table(result, billing="hourly", test=False):
    """Retrieve the total recurring fee of the items prices"""
    title = "OrderId: %s" % (result.get('orderId', 'No order placed'))
    table = formatting.Table(['Cost', 'Description'], title=title)
    table.align['Cost'] = 'r'
    table.align['Description'] = 'l'
    total = 0.000
    if test:
        prices = result['prices']
    else:
        prices = result['orderDetails']['prices']

    for item in prices:
        rate = 0.000
        if billing == "hourly":
            rate += float(item.get('hourlyRecurringFee', 0.000))
        else:
            rate += float(item.get('recurringFee', 0.000))
        total += rate
        table.add_row([rate, item['item']['description']])
    table.add_row(["%.3f" % total, "Total %s cost" % billing])
    return table


def _build_guest_table(result):
    table = formatting.Table(['ID', 'FQDN', 'guid', 'Order Date'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'
    virtual_guests = utils.lookup(result, 'orderDetails', 'virtualGuests')
    for guest in virtual_guests:
        table.add_row([guest['id'], guest['fullyQualifiedDomainName'], guest['globalIdentifier'], result['orderDate']])
    return table


def _validate_args(env, args):
    """Raises an ArgumentError if the given arguments are not valid."""

    if all([args['cpu'], args['flavor']]):
        raise exceptions.ArgumentError(
            '[-c | --cpu] not allowed with [-f | --flavor]')

    if all([args['memory'], args['flavor']]):
        raise exceptions.ArgumentError(
            '[-m | --memory] not allowed with [-f | --flavor]')

    if all([args['dedicated'], args['transient']]):
        raise exceptions.ArgumentError(
            '[--dedicated] not allowed with [--transient]')

    if all([args['dedicated'], args['flavor']]):
        raise exceptions.ArgumentError(
            '[-d | --dedicated] not allowed with [-f | --flavor]')

    if all([args['host_id'], args['flavor']]):
        raise exceptions.ArgumentError(
            '[-h | --host-id] not allowed with [-f | --flavor]')

    if args['transient'] and args['billing'] == 'monthly':
        raise exceptions.ArgumentError(
            '[--transient] not allowed with [--billing monthly]')

    if all([args['userdata'], args['userfile']]):
        raise exceptions.ArgumentError(
            '[-u | --userdata] not allowed with [-F | --userfile]')

    image_args = [args['os'], args['image']]
    if all(image_args):
        raise exceptions.ArgumentError(
            '[-o | --os] not allowed with [--image]')

    while not any([args['os'], args['image']]):
        args['os'] = env.input("Operating System Code", default="", show_default=False)
        if not args['os']:
            args['image'] = env.input("Image", default="", show_default=False)
