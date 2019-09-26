"""List firewalls."""
# :license: MIT, see LICENSE for more details.

import os
import subprocess
import tempfile

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import firewall
from SoftLayer.CLI import formatting

DELIMITER = "=========================================\n"


def parse_rules(content=None):
    """Helper to parse the input from the user into a list of rules.

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


def open_editor(rules=None, content=None):
    """Helper to open an editor for editing the firewall rules.

    This method takes two parameters, if content is provided,
    that means that submitting the rules failed and we are allowing
    the user to re-edit what they provided. If content is not provided, the
    rules retrieved from the firewall will be displayed to the user.

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


def get_formatted_rule(rule=None):
    """Helper to format the rule into a user friendly format.

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


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Edit firewall rules."""

    mgr = SoftLayer.FirewallManager(env.client)

    firewall_type, firewall_id = firewall.parse_id(identifier)
    if firewall_type == 'vlan':
        orig_rules = mgr.get_dedicated_fwl_rules(firewall_id)
    else:
        orig_rules = mgr.get_standard_fwl_rules(firewall_id)
    # open an editor for the user to enter their rules
    edited_rules = open_editor(rules=orig_rules)
    env.out(edited_rules)
    if formatting.confirm("Would you like to submit the rules. "
                          "Continue?"):
        while True:
            try:
                rules = parse_rules(edited_rules)
                if firewall_type == 'vlan':
                    mgr.edit_dedicated_fwl_rules(firewall_id, rules)
                else:
                    mgr.edit_standard_fwl_rules(firewall_id, rules)
                break
            except (SoftLayer.SoftLayerError, ValueError) as error:
                env.out("Unexpected error({%s})" % (error))
                if formatting.confirm("Would you like to continue editing "
                                      "the rules. Continue?"):
                    edited_rules = open_editor(content=edited_rules)
                    env.out(edited_rules)
                    if formatting.confirm("Would you like to submit the "
                                          "rules. Continue?"):
                        continue
                    raise exceptions.CLIAbort('Aborted.')
                raise exceptions.CLIAbort('Aborted.')
        env.fout('Firewall updated!')
    else:
        raise exceptions.CLIAbort('Aborted.')
