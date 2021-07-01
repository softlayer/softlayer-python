"""Get Load Balancer as a Service details."""
import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Get Load Balancer as a Service details."""
    mgr = SoftLayer.LoadBalancerManager(env.client)
    _, lbid = mgr.get_lbaas_uuid_id(identifier)
    this_lb = mgr.get_lb(lbid)
    if this_lb.get('previousErrorText'):
        print(this_lb.get('previousErrorText'))
    table = lbaas_table(this_lb)

    env.fout(table)


def lbaas_table(this_lb):
    """Generates a table from a list of LBaaS devices"""
    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'
    table.add_row(['Id', this_lb.get('id')])
    table.add_row(['UUI', this_lb.get('uuid')])
    table.add_row(['Address', this_lb.get('address')])
    table.add_row(['Location', utils.lookup(this_lb, 'datacenter', 'longName')])
    table.add_row(['Description', this_lb.get('description')])
    table.add_row(['Name', this_lb.get('name')])
    table.add_row(['Status', "{} / {}".format(this_lb.get('provisioningStatus'), this_lb.get('operatingStatus'))])

    # https://sldn.softlayer.com/reference/datatypes/SoftLayer_Network_LBaaS_HealthMonitor/
    hp_table = formatting.Table(['UUID', 'Interval', 'Retries', 'Type', 'Timeout', 'Modify', 'Active'])
    for health in this_lb.get('healthMonitors', []):
        hp_table.add_row([
            health.get('uuid'),
            health.get('interval'),
            health.get('maxRetries'),
            health.get('monitorType'),
            health.get('timeout'),
            utils.clean_time(health.get('modifyDate')),
            health.get('provisioningStatus')
        ])
    table.add_row(['Checks', hp_table])

    # https://sldn.softlayer.com/reference/datatypes/SoftLayer_Network_LBaaS_L7Pool/
    l7_table = formatting.Table(['Id', 'UUID', 'Balancer', 'Name', 'Protocol', 'Modify', 'Active'])
    for layer7 in this_lb.get('l7Pools', []):
        l7_table.add_row([
            layer7.get('id'),
            layer7.get('uuid'),
            layer7.get('loadBalancingAlgorithm'),
            layer7.get('name'),
            layer7.get('protocol'),
            utils.clean_time(layer7.get('modifyDate')),
            layer7.get('provisioningStatus')
        ])
    table.add_row(['L7 Pools', l7_table])

    pools = {}
    # https://sldn.softlayer.com/reference/datatypes/SoftLayer_Network_LBaaS_Listener/
    listener_table = formatting.Table(['UUID', 'Max Connection', 'Mapping', 'Balancer', 'Modify', 'Active'])
    for listener in this_lb.get('listeners', []):
        pool = listener.get('defaultPool')
        priv_map = "{}:{}".format(pool['protocol'], pool['protocolPort'])
        pools[pool['uuid']] = priv_map
        mapping = "{}:{} -> {}".format(listener.get('protocol'), listener.get('protocolPort'), priv_map)
        listener_table.add_row([
            listener.get('uuid'),
            listener.get('connectionLimit', 'None'),
            mapping,
            pool.get('loadBalancingAlgorithm', 'None'),
            utils.clean_time(listener.get('modifyDate')),
            listener.get('provisioningStatus')
        ])
    table.add_row(['Pools', listener_table])

    # https://sldn.softlayer.com/reference/datatypes/SoftLayer_Network_LBaaS_Member/
    member_col = ['UUID', 'Address', 'Weight', 'Modify', 'Active']
    for uuid in pools.values():
        member_col.append(uuid)
    member_table = formatting.Table(member_col)
    for member in this_lb.get('members', []):
        row = [
            member.get('uuid'),
            member.get('address'),
            member.get('weight'),
            utils.clean_time(member.get('modifyDate')),
            member.get('provisioningStatus')
        ]
        for uuid in pools:
            row.append(get_member_hp(this_lb.get('health'), member.get('uuid'), uuid))
        member_table.add_row(row)
    table.add_row(['Members', member_table])

    # https://sldn.softlayer.com/reference/datatypes/SoftLayer_Network_LBaaS_SSLCipher/
    ssl_table = formatting.Table(['Id', 'Name'])
    for ssl in this_lb.get('sslCiphers', []):
        ssl_table.add_row([ssl.get('id'), ssl.get('name')])
    table.add_row(['Ciphers', ssl_table])
    return table


def get_member_hp(checks, member_uuid, pool_uuid):
    """Helper function to find a members health in a given pool

    :param checks list: https://sldn.softlayer.com/reference/datatypes/SoftLayer_Network_LBaaS_Pool/#healthMonitor
    :param member_uuid: server UUID we are looking for
    :param pool_uuid: Connection pool uuid to search for
    """
    status = "---"
    for check in checks:
        if check.get('poolUuid') == pool_uuid:
            for hp_member in check.get('membersHealth'):
                if hp_member.get('uuid') == member_uuid:
                    status = hp_member.get('status')

    return status
