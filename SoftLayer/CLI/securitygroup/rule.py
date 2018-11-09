"""Manage security group rules."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting

COLUMNS = ['id',
           'remoteIp',
           'remoteGroupId',
           'direction',
           'ethertype',
           'portRangeMin',
           'portRangeMax',
           'protocol',
           'createDate',
           'modifyDate']


@click.command()
@click.argument('securitygroup_id')
@click.option('--sortby',
              help='Column to sort by',
              type=click.Choice(COLUMNS))
@environment.pass_env
def rule_list(env, securitygroup_id, sortby):
    """List security group rules."""

    mgr = SoftLayer.NetworkManager(env.client)

    table = formatting.Table(COLUMNS)
    table.sortby = sortby

    rules = mgr.list_securitygroup_rules(securitygroup_id)
    for rule in rules:
        port_min = rule.get('portRangeMin')
        port_max = rule.get('portRangeMax')
        if port_min is None:
            port_min = formatting.blank()
        if port_max is None:
            port_max = formatting.blank()

        table.add_row([
            rule['id'],
            rule.get('remoteIp') or formatting.blank(),
            rule.get('remoteGroupId') or formatting.blank(),
            rule['direction'],
            rule.get('ethertype') or formatting.blank(),
            port_min,
            port_max,
            rule.get('protocol') or formatting.blank(),
            rule.get('createDate') or formatting.blank(),
            rule.get('modifyDate') or formatting.blank()
        ])

    env.fout(table)


@click.command()
@click.argument('securitygroup_id')
@click.option('--remote-ip', '-r',
              help='The remote IP/CIDR to enforce')
@click.option('--remote-group', '-s', type=click.INT,
              help='The ID of the remote security group to enforce')
@click.option('--direction', '-d',
              help=('The direction of traffic to enforce '
                    '(ingress, egress)'))
@click.option('--ethertype', '-e',
              help='The ethertype (IPv4 or IPv6) to enforce')
@click.option('--port-max', '-M', type=click.INT,
              help=('The upper port bound to enforce. When the protocol is ICMP, '
                    'this specifies the ICMP code to permit'))
@click.option('--port-min', '-m', type=click.INT,
              help=('The lower port bound to enforce. When the protocol is ICMP, '
                    'this specifies the ICMP type to permit'))
@click.option('--protocol', '-p',
              help='The protocol (icmp, tcp, udp) to enforce')
@environment.pass_env
def add(env, securitygroup_id, remote_ip, remote_group,
        direction, ethertype, port_max, port_min, protocol):
    """Add a security group rule to a security group.

    \b
    Examples:
        # Add an SSH rule (TCP port 22) to a security group
        slcli sg rule-add 384727 \\
            --direction ingress \\
            --protocol tcp \\
            --port-min 22 \\
            --port-max 22

    \b
        # Add a ping rule (ICMP type 8 code 0) to a security group
        slcli sg rule-add 384727 \\
            --direction ingress \\
            --protocol icmp \\
            --port-min 8 \\
            --port-max 0
    """
    mgr = SoftLayer.NetworkManager(env.client)

    ret = mgr.add_securitygroup_rule(securitygroup_id, remote_ip, remote_group,
                                     direction, ethertype, port_max,
                                     port_min, protocol)

    if not ret:
        raise exceptions.CLIAbort("Failed to add security group rule")


@click.command()
@click.argument('securitygroup_id')
@click.argument('rule_id')
@click.option('--remote-ip', '-r',
              help='The remote IP/CIDR to enforce')
@click.option('--remote-group', '-s',
              help='The ID of the remote security group to enforce')
@click.option('--direction', '-d',
              help='The direction of traffic to enforce')
@click.option('--ethertype', '-e',
              help='The ethertype (IPv4 or IPv6) to enforce')
@click.option('--port-max', '-M',
              help='The upper port bound to enforce')
@click.option('--port-min', '-m',
              help='The lower port bound to enforce')
@click.option('--protocol', '-p',
              help='The protocol (icmp, tcp, udp) to enforce')
@environment.pass_env
def edit(env, securitygroup_id, rule_id, remote_ip, remote_group,
         direction, ethertype, port_max, port_min, protocol):
    """Edit a security group rule in a security group."""
    mgr = SoftLayer.NetworkManager(env.client)

    data = {}
    if remote_ip:
        data['remote_ip'] = remote_ip
    if remote_group:
        data['remote_group'] = remote_group
    if direction:
        data['direction'] = direction
    if ethertype:
        data['ethertype'] = ethertype
    if port_max is not None:
        data['port_max'] = port_max
    if port_min is not None:
        data['port_min'] = port_min
    if protocol:
        data['protocol'] = protocol

    if not mgr.edit_securitygroup_rule(securitygroup_id, rule_id, **data):
        raise exceptions.CLIAbort("Failed to edit security group rule")


@click.command()
@click.argument('securitygroup_id')
@click.argument('rule_id')
@environment.pass_env
def remove(env, securitygroup_id, rule_id):
    """Remove a rule from a security group."""
    mgr = SoftLayer.NetworkManager(env.client)
    if not mgr.remove_securitygroup_rule(securitygroup_id, rule_id):
        raise exceptions.CLIAbort("Failed to remove security group rule")
