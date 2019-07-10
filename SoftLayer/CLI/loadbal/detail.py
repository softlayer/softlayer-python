"""Get Load Balancer as a Service details."""
import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils
from pprint import pprint as pp 

@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Get Load Balancer as a Service details."""
    mgr = SoftLayer.LoadBalancerManager(env.client)

    lb = mgr.get_lb(identifier)
    pp(lb)
    table = lbaas_table(lb)

    env.fout(table)


def lbaas_table(lb):
    """Generates a table from a list of LBaaS devices"""
    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'
    table.add_row(['Id', lb.get('id')])
    table.add_row(['UUI', lb.get('uuid')])
    table.add_row(['Address', lb.get('address')])
    table.add_row(['Location', utils.lookup(lb, 'datacenter', 'longName')])
    table.add_row(['Description', lb.get('description')])
    table.add_row(['Name', lb.get('name')])
    table.add_row(['Status', "{} / {}".format(lb.get('provisioningStatus'), lb.get('operatingStatus'))])

    # https://sldn.softlayer.com/reference/datatypes/SoftLayer_Network_LBaaS_HealthMonitor/
    hp_table = formatting.Table(['UUID', 'Interval', 'Retries', 'Type', 'Timeout', 'Modify', 'Active'])
    for hp in lb.get('healthMonitors', []):
        hp_table.add_row([
            hp.get('uuid'),
            hp.get('interval'),
            hp.get('maxRetries'),
            hp.get('monitorType'),
            hp.get('timeout'),
            utils.clean_time(hp.get('modifyDate')),
            hp.get('provisioningStatus')
        ])
    table.add_row(['Checks', hp_table])

    # https://sldn.softlayer.com/reference/datatypes/SoftLayer_Network_LBaaS_L7Pool/
    l7_table = formatting.Table(['UUID', 'Balancer', 'Name', 'Protocol', 'Modify', 'Active' ])
    for l7 in lb.get('l7Pools', []):
        l7_table.add_row([
            l7.get('uuid'),
            l7.get('loadBalancingAlgorithm'),
            l7.get('name'),
            l7.get('protocol'),
            utils.clean_time(l7.get('modifyDate')),
            l7.get('provisioningStatus')
        ])
    table.add_row(['L7 Pools', l7_table])

    pools = {}
    # https://sldn.softlayer.com/reference/datatypes/SoftLayer_Network_LBaaS_Listener/
    listener_table = formatting.Table(['UUID', 'Max Connection', 'Mapping', 'Balancer', 'Modify', 'Active'])
    for listener in lb.get('listeners', []):
        pool = listener.get('defaultPool')
        priv_map = "{}:{}".format(pool['protocol'], pool['protocolPort'])
        pools[pool['uuid']] = priv_map
        mapping = "{}:{} -> {}".format(listener.get('protocol'), listener.get('protocolPort'), priv_map)
        pool_table = formatting.Table(['Address', ])
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
    for uuid in pools.keys():
        member_col.append(pools[uuid])
    member_table = formatting.Table(member_col)
    for member in lb.get('members', []):
        row = [
            member.get('uuid'),
            member.get('address'),
            member.get('weight'),
            utils.clean_time(member.get('modifyDate')),
            member.get('provisioningStatus')
        ]
        for uuid in pools.keys():
            row.append(getMemberHp(lb.get('health'), member.get('uuid'), uuid))
        member_table.add_row(row)
    table.add_row(['Members',member_table])

    # https://sldn.softlayer.com/reference/datatypes/SoftLayer_Network_LBaaS_SSLCipher/
    ssl_table = formatting.Table(['Id', 'Name'])
    for ssl in lb.get('sslCiphers', []):
        ssl_table.add_row([ssl.get('id'), ssl.get('name')])
    table.add_row(['Ciphers', ssl_table])
    return table

def getMemberHp(checks, member_uuid, pool_uuid):
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