"""Order/Create a scale group."""
# :license: MIT, see LICENSE for more details.

import click
from SoftLayer import utils

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer.managers.autoscale import AutoScaleManager


@click.command()
@click.option('--name', help="Scale group's name.")
@click.option('--cooldown', type=click.INT,
              help="The number of seconds this group will wait after lastActionDate before performing another action.")
@click.option('--min', 'minimum', type=click.INT, help="Set the minimum number of guests")
@click.option('--max', 'maximum', type=click.INT, help="Set the maximum number of guests")
@click.option('--regional', type=click.INT,
              help="The identifier of the regional group this scaling group is assigned to.")
@click.option('--postinstall', '-i', help="Post-install script to download")
@click.option('--os', '-o', help="OS install code. Tip: you can specify <OS>_LATEST")
@click.option('--datacenter', '-d', required=True, prompt=True, help="Datacenter shortname")
@click.option('--hostname', '-H', required=True, prompt=True, help="Host portion of the FQDN")
@click.option('--domain', '-D', required=True, prompt=True, help="Domain portion of the FQDN")
@click.option('--cpu', type=click.INT, help="Number of CPUs for new guests (existing not effected")
@click.option('--memory', type=click.INT, help="RAM in MB or GB for new guests (existing not effected")
@click.option('--policy-relative', help="The type of scale to perform(ABSOLUTE, PERCENT, RELATIVE).")
@click.option('--termination-policy',
              help="The termination policy for the group(CLOSEST_TO_NEXT_CHARGE=1, NEWEST=2, OLDEST=3).")
@click.option('--policy-name', help="Collection of policies for this group. This can be empty.")
@click.option('--policy-amount', help="The number to scale by. This number has different meanings based on type.")
@click.option('--userdata', help="User defined metadata string")
@helpers.multi_option('--key', '-k', help="SSH keys to add to the root user")
@helpers.multi_option('--disk', help="Disk sizes")
@environment.pass_env
def cli(env, **args):
    """Order/Create a scale group."""
    scale = AutoScaleManager(env.client)
    network = SoftLayer.NetworkManager(env.client)

    datacenter = network.get_datacenter(args.get('datacenter'))

    ssh_keys = []
    for key in args.get('key'):
        resolver = SoftLayer.SshKeyManager(env.client).resolve_ids
        key_id = helpers.resolve_id(resolver, key, 'SshKey')
        ssh_keys.append(key_id)
    scale_actions = [
        {
            "amount": args['policy_amount'],
            "scaleType": args['policy_relative']
        }
    ]
    policy_template = {
        'name': args['policy_name'],
        'policies': scale_actions

    }
    policies = []

    block = []
    number_disk = 0
    for guest_disk in args['disk']:
        disks = {'diskImage': {'capacity': guest_disk}, 'device': number_disk}
        block.append(disks)
        number_disk += 1

    virt_template = {
        'localDiskFlag': False,
        'domain': args['domain'],
        'hostname': args['hostname'],
        'sshKeys': ssh_keys,
        'postInstallScriptUri': args.get('postinstall'),
        'operatingSystemReferenceCode': args['os'],
        'maxMemory': args.get('memory'),
        'datacenter': {'id': datacenter[0]['id']},
        'startCpus': args.get('cpu'),
        'blockDevices': block,
        'hourlyBillingFlag': True,
        'privateNetworkOnlyFlag': False,
        'networkComponents': [{'maxSpeed': 100}],
        'typeId': 1,
        'userData': [{
            'value': args.get('userdata')
        }],
        'networkVlans': [],

    }

    order = {
        'name': args['name'],
        'cooldown': args['cooldown'],
        'maximumMemberCount': args['maximum'],
        'minimumMemberCount': args['minimum'],
        'regionalGroupId': args['regional'],
        'suspendedFlag': False,
        'balancedTerminationFlag': False,
        'virtualGuestMemberTemplate': virt_template,
        'virtualGuestMemberCount': 0,
        'policies': policies.append(utils.clean_dict(policy_template)),
        'terminationPolicyId': args['termination_policy']
    }

    if not (env.skip_confirmations or formatting.confirm(
            "This action will incur charges on your account. Continue?")):
        raise exceptions.CLIAbort('Aborting scale group order.')
    else:
        result = scale.create(order)

        table = formatting.KeyValueTable(['name', 'value'])
        table.align['name'] = 'r'
        table.align['value'] = 'l'
        table.add_row(['Id', result['id']])
        table.add_row(['Created', result['createDate']])
        table.add_row(['Name', result['name']])
        table.add_row(['Virtual Guest Id', result['virtualGuestMembers'][0]['virtualGuest']['id']])
        table.add_row(['Virtual Guest domain', result['virtualGuestMembers'][0]['virtualGuest']['domain']])
        table.add_row(['Virtual Guest hostname', result['virtualGuestMembers'][0]['virtualGuest']['hostname']])
        output = table

    env.fout(output)
