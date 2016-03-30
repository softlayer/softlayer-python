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
        'cpu': like_details['maxCpu'],
        'memory': '%smb' % like_details['maxMemory'],
        'hourly': like_details['hourlyBillingFlag'],
        'datacenter': like_details['datacenter']['name'],
        'network': like_details['networkComponents'][0]['maxSpeed'],
        'userdata': like_details['userData'] or None,
        'postinstall': like_details.get('postInstallScriptUri'),
        'dedicated': like_details['dedicatedAccountHostOnlyFlag'],
        'private': like_details['privateNetworkOnlyFlag'],
    }

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
        "hourly": args['billing'] == 'hourly',
        "cpus": args['cpu'],
        "domain": args['domain'],
        "hostname": args['hostname'],
        "private": args['private'],
        "dedicated": args['dedicated'],
        "disks": args['disk'],
        "local_disk": not args['san'],
    }

    data["memory"] = args['memory']

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

    if args.get('tag'):
        data['tags'] = ','.join(args['tag'])

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
              help="Number of CPU cores",
              type=click.INT,
              required=True,
              prompt=True)
@click.option('--memory', '-m',
              help="Memory in mebibytes",
              type=virt.MEM_TYPE,
              required=True,
              prompt=True)
@click.option('--datacenter', '-d',
              help="Datacenter shortname",
              required=True,
              prompt=True)
@click.option('--os', '-o',
              help="OS install code. Tip: you can specify <OS>_LATEST")
@click.option('--image',
              help="Image ID. See: 'slcli image list' for reference")
@click.option('--billing',
              type=click.Choice(['hourly', 'monthly']),
              default='hourly',
              show_default=True,
              help="Billing rate")
@click.option('--dedicated/--public',
              is_flag=True,
              help="Create a dedicated Virtual Server (Private Node)")
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
        total_monthly = 0.0
        total_hourly = 0.0

        table = formatting.Table(['Item', 'cost'])
        table.align['Item'] = 'r'
        table.align['cost'] = 'r'

        for price in result['prices']:
            total_monthly += float(price.get('recurringFee', 0.0))
            total_hourly += float(price.get('hourlyRecurringFee', 0.0))
            if args.get('billing') == 'hourly':
                rate = "%.2f" % float(price['hourlyRecurringFee'])
            elif args.get('billing') == 'monthly':
                rate = "%.2f" % float(price['recurringFee'])

            table.add_row([price['item']['description'], rate])

        total = 0
        if args.get('billing') == 'hourly':
            total = total_hourly
        elif args.get('billing') == 'monthly':
            total = total_monthly

        billing_rate = 'monthly'
        if args.get('billing') == 'hourly':
            billing_rate = 'hourly'
        table.add_row(['Total %s cost' % billing_rate, "%.2f" % total])
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


def _validate_args(env, args):
    """Raises an ArgumentError if the given arguments are not valid."""

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
