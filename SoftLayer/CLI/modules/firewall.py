"""
usage: sl firewall [<command>] [<args>...] [options]

Firewall rule and security management

The available commands are:
  add    Add a new firewall
  cancel Cancel an existing firewall
  detail Provide details about a particular firewall
  edit   Edit the rules of a particular firewall
  list   List active firewalls - both dedicated and shared

"""
# :license: MIT, see LICENSE for more details.

from __future__ import print_function
import os
import subprocess
import tempfile

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer import utils

DELIMITER = "=========================================\n"


def get_ids(input_id):
    """ Helper package to retrieve the actual IDs
    :param input_id: the ID provided by the user
    :returns: A list of valid IDs
    """
    key_value = input_id.split(':')

    if len(key_value) != 2:
        raise exceptions.CLIAbort(
            'Invalid ID %s: ID should be of the form xxx:yyy' % input_id)
    return key_value


def print_package_info(package):
    """ Helper package to print the firewall price.

    :param dict package: A dictionary representing the firewall package
    """
    print("******************")
    print("Product: %s" % package[0]['description'])
    print("Price: %s$ monthly" % package[0]['prices'][0]['recurringFee'])
    print("******************")
    return


def has_firewall_component(server):
    """ Helper to determine whether or not a server has a firewall.

    :param dict server: A dictionary representing a server
    :returns: True if the Server has a firewall.
    """
    if server['status'] != 'no_edit':
        return True

    return False


def get_rules_table(rules):
    """ Helper to format the rules into a table

    :param list rules: A list containing the rules of the firewall
    :returns: a formatted table of the firewall rules
    """
    table = formatting.Table(['#', 'action', 'protocol', 'src_ip', 'src_mask',
                              'dest', 'dest_mask'])
    table.sortby = '#'
    for rule in rules:
        table.add_row([
            rule['orderValue'],
            rule['action'],
            rule['protocol'],
            rule['sourceIpAddress'],
            rule['sourceIpSubnetMask'],
            '%s:%s-%s' % (rule['destinationIpAddress'],
                          rule['destinationPortRangeStart'],
                          rule['destinationPortRangeEnd']),
            rule['destinationIpSubnetMask']])
    return table


def get_formatted_rule(rule=None):
    """ Helper to format the rule into a user friendly format
        for editing purposes

    :param dict rule: A dict containing one rule of the firewall
    :returns: a formatted string that get be pushed into the editor
    """
    rule = rule or {}
    return ('action: %s\n'
            'protocol: %s\n'
            'source_ip_address: %s\n'
            'source_ip_subnet_mask: %s\n'
            'destination_ip_address: %s\n'
            'destination_ip_subnet_mask: %s\n'
            'destination_port_range_start: %s\n'
            'destination_port_range_end: %s\n'
            'version: %s\n'
            % (rule.get('action', 'permit'),
               rule.get('protocol', 'tcp'),
               rule.get('sourceIpAddress', 'any'),
               rule.get('sourceIpSubnetMask', '255.255.255.255'),
               rule.get('destinationIpAddress', 'any'),
               rule.get('destinationIpSubnetMask', '255.255.255.255'),
               rule.get('destinationPortRangeStart', 1),
               rule.get('destinationPortRangeEnd', 1),
               rule.get('version', 4)))


def open_editor(rules=None, content=None):
    """ Helper to open an editor for editing the firewall rules
        This method takes two parameters, if content is provided,
        that means that submitting the rules failed and we are allowing
        the user to re-edit what they provided.
        If content is not provided, the rules retrieved from the firewall
        will be displayed to the user.

    :param list rules: A list containing the rules of the firewall
    :param string content: the content that the user provided in the editor
    :returns: a formatted string that get be pushed into the editor
    """

    # Let's get the default EDITOR of the environment,
    # use nano if none is specified
    editor = os.environ.get('EDITOR', 'nano')

    with tempfile.NamedTemporaryFile(suffix=".tmp") as tfile:

        if content:
            # if content is provided, just display it as is
            tfile.write(content)
            tfile.flush()
            subprocess.call([editor, tfile.name])
            tfile.seek(0)
            data = tfile.read()
            return data

        if not rules:
            # if the firewall has no rules, provide a template
            tfile.write(DELIMITER)
            tfile.write(get_formatted_rule())
        else:
            # if the firewall has rules, display those to the user
            for rule in rules:
                tfile.write(DELIMITER)
                tfile.write(get_formatted_rule(rule))
        tfile.write(DELIMITER)
        tfile.flush()
        subprocess.call([editor, tfile.name])
        tfile.seek(0)
        data = tfile.read()
        return data

    return


def parse_rules(content=None):
    """ Helper to parse the input from the user into a list of rules.

    :param string content: the content of the editor
    :returns: a list of rules
    """
    rules = content.split(DELIMITER)
    parsed_rules = list()
    order = 1
    for rule in rules:
        if rule.strip() == '':
            continue
        parsed_rule = {}
        lines = rule.split("\n")
        parsed_rule['orderValue'] = order
        order += 1
        for line in lines:
            if line.strip() == '':
                continue
            key_value = line.strip().split(':')
            key = key_value[0].strip()
            value = key_value[1].strip()
            if key == 'action':
                parsed_rule['action'] = value
            elif key == 'protocol':
                parsed_rule['protocol'] = value
            elif key == 'source_ip_address':
                parsed_rule['sourceIpAddress'] = value
            elif key == 'source_ip_subnet_mask':
                parsed_rule['sourceIpSubnetMask'] = value
            elif key == 'destination_ip_address':
                parsed_rule['destinationIpAddress'] = value
            elif key == 'destination_ip_subnet_mask':
                parsed_rule['destinationIpSubnetMask'] = value
            elif key == 'destination_port_range_start':
                parsed_rule['destinationPortRangeStart'] = int(value)
            elif key == 'destination_port_range_end':
                parsed_rule['destinationPortRangeEnd'] = int(value)
            elif key == 'version':
                parsed_rule['version'] = int(value)
        parsed_rules.append(parsed_rule)
    return parsed_rules


class FWList(environment.CLIRunnable):
    """
usage: sl firewall list [options]

List active firewalls
"""
    action = 'list'

    def execute(self, args):
        mgr = SoftLayer.FirewallManager(self.client)
        table = formatting.Table(['firewall id',
                                  'type',
                                  'features',
                                  'server/vlan id'])
        fwvlans = mgr.get_firewalls()
        dedicated_firewalls = [firewall for firewall in fwvlans
                               if firewall['dedicatedFirewallFlag']]

        for vlan in dedicated_firewalls:
            features = []
            if vlan['highAvailabilityFirewallFlag']:
                features.append('HA')

            if features:
                feature_list = formatting.listing(features, separator=',')
            else:
                feature_list = formatting.blank()

            table.add_row([
                'vlan:%s' % vlan['networkVlanFirewall']['id'],
                'VLAN - dedicated',
                feature_list,
                vlan['id']
            ])

        shared_vlan = [firewall for firewall in fwvlans
                       if not firewall['dedicatedFirewallFlag']]
        for vlan in shared_vlan:
            vs_firewalls = [guest
                            for guest in vlan['firewallGuestNetworkComponents']
                            if has_firewall_component(guest)]

            for firewall in vs_firewalls:
                table.add_row([
                    'cci:%s' % firewall['id'],
                    'CCI - standard',
                    '-',
                    firewall['guestNetworkComponent']['guest']['id']
                ])

            server_firewalls = [server
                                for server in vlan['firewallNetworkComponents']
                                if has_firewall_component(server)]

            for firewall in server_firewalls:
                table.add_row([
                    'server:%s' % firewall['id'],
                    'Server - standard',
                    '-',
                    utils.lookup(firewall,
                                 'networkComponent',
                                 'downlinkComponent',
                                 'hardwareId')
                ])

        return table


class FWCancel(environment.CLIRunnable):
    """
usage: sl firewall cancel <identifier> [options]

Cancels a firewall

Options:
  --really     Whether to skip the confirmation prompt

"""
    action = 'cancel'
    options = ['really']

    def execute(self, args):
        mgr = SoftLayer.FirewallManager(self.client)
        input_id = args.get('<identifier>')
        key_value = get_ids(input_id)
        firewall_id = int(key_value[1])

        if args['--really'] or formatting.confirm("This action will cancel a "
                                                  "firewall from your account."
                                                  " Continue?"):
            if key_value[0] in ['cci', 'server']:
                mgr.cancel_firewall(firewall_id, dedicated=False)
            elif key_value[0] == 'vlan':
                mgr.cancel_firewall(firewall_id, dedicated=True)
            return 'Firewall with id %s is being cancelled!' % input_id
        else:
            raise exceptions.CLIAbort('Aborted.')


class FWAdd(environment.CLIRunnable):
    """
usage: sl firewall add <identifier> (--cci | --vlan | --server) [options]

Adds a firewall of type either standard (cci or server) or dedicated(vlan)
Options:
  --cci     creates a standard firewall for a CCI
  --vlan    creates a dedicated firewall for a VLAN
  --server  creates a standard firewall for a server
  --ha      whether HA will be on or off - only for dedicated
  --really  whether to skip the confirmation prompt
"""
    action = 'add'
    options = ['really', 'ha']

    def execute(self, args):
        mgr = SoftLayer.FirewallManager(self.client)
        input_id = helpers.resolve_id(
            mgr.resolve_ids, args.get('<identifier>'), 'firewall')
        ha_support = args.get('--ha', False)
        if not args['--really']:
            if args['--vlan']:
                pkg = mgr.get_dedicated_package(ha_enabled=ha_support)
            elif args['--cci']:
                pkg = mgr.get_standard_package(input_id)
            elif args['--server']:
                pkg = mgr.get_standard_package(input_id, is_cci=False)

            if not pkg:
                return "Unable to add firewall - Is network public enabled?"
            print_package_info(pkg)

            if not formatting.confirm("This action will incur charges on your "
                                      "account. Continue?"):
                raise exceptions.CLIAbort('Aborted.')

        if args['--vlan']:
            mgr.add_vlan_firewall(input_id, ha_enabled=ha_support)
        elif args['--cci']:
            mgr.add_standard_firewall(input_id, is_cci=True)
        elif args['--server']:
            mgr.add_standard_firewall(input_id, is_cci=False)

        return "Firewall is being created!"


class FWDetails(environment.CLIRunnable):
    """
usage: sl firewall detail <identifier> [options]

Get firewall details
"""
    action = 'detail'

    def execute(self, args):
        mgr = SoftLayer.FirewallManager(self.client)
        input_id = args.get('<identifier>')

        key_value = get_ids(input_id)
        if key_value[0] == 'vlan':
            rules = mgr.get_dedicated_fwl_rules(key_value[1])
        else:
            rules = mgr.get_standard_fwl_rules(key_value[1])

        return get_rules_table(rules)


class FWEdit(environment.CLIRunnable):
    """
usage: sl firewall edit <identifier> [options]

Edit the rules for a firewall
"""
    action = 'edit'

    def execute(self, args):
        mgr = SoftLayer.FirewallManager(self.client)
        input_id = args.get('<identifier>')

        key_value = get_ids(input_id)
        firewall_id = int(key_value[1])
        if key_value[0] == 'vlan':
            orig_rules = mgr.get_dedicated_fwl_rules(firewall_id)
        else:
            orig_rules = mgr.get_standard_fwl_rules(firewall_id)
        # open an editor for the user to enter their rules
        edited_rules = open_editor(rules=orig_rules)
        print(edited_rules)
        if formatting.confirm("Would you like to submit the rules. "
                              "Continue?"):
            while True:
                try:
                    rules = parse_rules(edited_rules)
                    if key_value[0] == 'vlan':
                        rules = mgr.edit_dedicated_fwl_rules(firewall_id,
                                                             rules)
                    else:
                        rules = mgr.edit_standard_fwl_rules(firewall_id,
                                                            rules)
                    break
                except (SoftLayer.SoftLayerError, ValueError) as error:
                    print("Unexpected error({%s})" % (error))
                    if formatting.confirm("Would you like to continue editing "
                                          "the rules. Continue?"):
                        edited_rules = open_editor(content=edited_rules)
                        print(edited_rules)
                        if formatting.confirm("Would you like to submit the "
                                              "rules. Continue?"):
                            continue
                        else:
                            raise exceptions.CLIAbort('Aborted.')
                    else:
                        raise exceptions.CLIAbort('Aborted.')
                    return 'Firewall updated!'
        else:
            raise exceptions.CLIAbort('Aborted.')
