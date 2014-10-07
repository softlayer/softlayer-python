"""Manage, delete, order compute instances"""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer.CLI import template
from SoftLayer import utils

import click


@click.command(epilog="See 'sl vs create-options' for valid options")
@click.option('--cpu', '-c', help="Number of CPU cores", type=click.INT)
@click.option('--domain', '-D', help="Domain portion of the FQDN")
@click.option('--hostname', '-H', help="Host portion of the FQDN")
@click.option('--image', '-H',
              help="Image GUID. See: 'sl image list' for reference")
@click.option('--memory', '-m', help="Memory in mebibytes", type=click.INT)
@click.option('--os', '-o',
              help="OS install code. Tip: you can specify <OS>_LATEST")
@click.option('--hourly/--monthly',
              help="Hourly or monthly rate instance type")
@click.option('--datacenter', '-d', help="Datacenter shortname")
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
              is_flag=True,
              help="Exports options to a template file")
@click.option('--userfile', '-F',
              help="Read userdata from file",
              type=click.Path(exists=True, readable=True, resolve_path=True))
@click.option('--postinstall', '-i', help="Post-install script to download")
@click.option('--keys', '-m',
              multiple=True,
              help="SSH keys to add to the root user")
@click.option('--disk', multiple=True, help="Disk sizes")
@click.option('--private',
              is_flag=True,
              help="Forces the VS to only have access the private network")
@click.option('--like',
              is_flag=True,
              help="Use the configuration from an existing VS")
@click.option('--network', '-n', help="Network port speed in Mbps")
@click.option('--template', '-t',
              help="A template file that defaults the command-line options",
              type=click.Path(exists=True, readable=True, resolve_path=True))
@click.option('--userdata', '-u', help="User defined metadata string")
@click.option('--vlan_public',
              help="The ID of the public VLAN on which you want the virtual "
              "server placed",
              type=click.INT)
@click.option('--vlan_private',
              help="The ID of the private VLAN on which you want the virtual "
                   "server placed",
              type=click.INT)
@click.option('--wait',
              help="Wait until VS is finished provisioning for up to X "
                   "seconds before returning",
              type=click.INT)
@environment.pass_env
def cli(env, **args):
    """Order/create virtual servers"""

    template.update_with_template_args(args, list_args=['disk', 'key'])
    vsi = SoftLayer.VSManager(env.client)
    _update_with_like_args(env.client, args)
    _validate_args(args)

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
            if args.get('hourly'):
                rate = "%.2f" % float(price['hourlyRecurringFee'])
            else:
                rate = "%.2f" % float(price['recurringFee'])

            table.add_row([price['item']['description'], rate])

        if args.get('hourly'):
            total = total_hourly
        else:
            total = total_monthly

        billing_rate = 'monthly'
        if args.get('hourly'):
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
        return 'Successfully exported options to a template file.'

    if do_create:
        if env.skip_confirmations or formatting.confirm(
                "This action will incur charges on your account. Continue?"):
            result = vsi.create_instance(**data)

            table = formatting.KeyValueTable(['name', 'value'])
            table.align['name'] = 'r'
            table.align['value'] = 'l'
            table.add_row(['id', result['id']])
            table.add_row(['created', result['createDate']])
            table.add_row(['guid', result['globalIdentifier']])
            output.append(table)

            if args.get('wait'):
                ready = vsi.wait_for_ready(
                    result['id'], int(args.get('wait') or 1))
                table.add_row(['ready', ready])
        else:
            raise exceptions.CLIAbort('Aborting virtual server order.')

    return output


def _validate_args(args):
    """ Raises an ArgumentError if the given arguments are not valid """
    req_params = ['hostname', 'domain', 'cpu', 'memory', 'datacenter', 'os']
    invalid_args = [k for k in req_params if args.get(k) is None]
    if invalid_args:
        raise exceptions.ArgumentError('Missing required options: %s'
                                       % ', '.join(invalid_args))

    if all([args['userdata'], args['userfile']]):
        raise exceptions.ArgumentError(
            '[-u | --userdata] not allowed with [-F | --userfile]')

    image_args = [args['os'], args['image']]
    if all(image_args):
        raise exceptions.ArgumentError(
            '[-o | --os] not allowed with [--image]')

    if not any(image_args):
        raise exceptions.ArgumentError(
            'One of [--os | --image] is required')


def _update_with_like_args(env, args):
    """ Update arguments with options taken from a currently running VS.

    :param VSManager args: A VSManager
    :param dict args: CLI arguments
    """
    if args['like']:
        vsi = SoftLayer.VSManager(env.client)
        vs_id = helpers.resolve_id(vsi.resolve_ids, args.pop('like'), 'VS')
        like_details = vsi.get_instance(vs_id)
        like_args = {
            'hostname': like_details['hostname'],
            'domain': like_details['domain'],
            'cpu': like_details['maxCpu'],
            'memory': like_details['maxMemory'],
            'hourly': like_details['hourlyBillingFlag'],
            'datacenter': like_details['datacenter']['name'],
            'network': like_details['networkComponents'][0]['maxSpeed'],
            'user-data': like_details['userData'] or None,
            'postinstall': like_details.get('postInstallScriptUri'),
            'dedicated': like_details['dedicatedAccountHostOnlyFlag'],
            'private': like_details['privateNetworkOnlyFlag'],
        }

        tag_refs = like_details.get('tagReferences', None)
        if tag_refs is not None and len(tag_refs) > 0:
            tags = ','.join([t['tag']['name'] for t in tag_refs])
            like_args['tag'] = tags

        # Handle mutually exclusive options
        like_image = utils.lookup(like_details,
                                  'blockDeviceTemplateGroup',
                                  'globalIdentifier')
        like_os = utils.lookup(like_details,
                               'operatingSystem',
                               'softwareLicense',
                               'softwareDescription',
                               'referenceCode')
        if like_image and not args.get('os'):
            like_args['image'] = like_image
        elif like_os and not args.get('image'):
            like_args['os'] = like_os

        # Merge like VS options with the options passed in
        for key, value in like_args.items():
            if args.get(key) in [None, False]:
                args[key] = value


def _parse_create_args(client, args):
    """ Converts CLI arguments to arguments that can be passed into
        VSManager.create_instance.

    :param dict args: CLI arguments
    """
    data = {
        "hourly": args['hourly'],
        "cpus": args['cpu'],
        "domain": args['domain'],
        "hostname": args['hostname'],
        "private": args['private'],
        "dedicated": args['dedicated'],
        "disks": args['disk'],
        "local_disk": not args['san'],
    }

    memory = args['memory']
    if memory < 1024:
        memory = memory * 1024

    data["memory"] = memory

    if args.get('os'):
        data['os_code'] = args['os']

    if args.get('image'):
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
        data['tag'] = args['tag']

    return data
