"""List Layer7 policies"""
import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@click.option('--protocol-id', '-p',
              required=False,
              type=int,
              help="Front-end Protocol identifier")
@environment.pass_env
def policies(env, protocol_id):
    """List policies of the front-end protocol (listener)."""
    mgr = SoftLayer.LoadBalancerManager(env.client)

    if protocol_id:
        l7policies = mgr.get_l7policies(protocol_id)
        table = generate_l7policies_table(l7policies, protocol_id)
    else:
        l7policies = mgr.get_all_l7policies()
        table = l7policies_table(l7policies)
    env.fout(table)


def generate_l7policies_table(l7policies, identifier):
    """Takes a list of Layer7 policies and makes a table"""
    table = formatting.Table([
        'Id', 'UUID', 'Name', 'Action', 'Redirect', 'Priority', 'Create Date'
    ], title=f"Layer7 policies - protocol ID {identifier}")

    table.align['Name'] = 'l'
    table.align['Action'] = 'l'
    table.align['Redirect'] = 'l'
    for l7policy in sorted(l7policies, key=lambda data: data.get('priority')):
        table.add_row([
            l7policy.get('id'),
            l7policy.get('uuid'),
            l7policy.get('name'),
            l7policy.get('action'),
            l7policy.get('redirectL7PoolId') or l7policy.get('redirectUrl') or formatting.blank(),
            l7policy.get('priority'),
            l7policy.get('createDate'),
        ])
    return table


def l7policies_table(listeners):
    """Takes a dict of (protocols: policies list) and makes a list of tables"""
    tables = []
    for listener_id, list_policy in listeners.items():
        tables.append(generate_l7policies_table(list_policy, listener_id))
    return tables
