"""Get Load balancer details."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import loadbal


@click.command()
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Get Load balancer details."""
    mgr = SoftLayer.LoadBalancerManager(env.client)

    _, loadbal_id = loadbal.parse_id(identifier)

    load_balancer = mgr.get_local_lb(loadbal_id)

    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'l'
    table.align['value'] = 'l'
    table.add_row(['ID', 'local:%s' % load_balancer['id']])
    table.add_row(['IP Address', load_balancer['ipAddress']['ipAddress']])
    name = load_balancer['loadBalancerHardware'][0]['datacenter']['name']
    table.add_row(['Datacenter', name])
    table.add_row(['Connections limit', load_balancer['connectionLimit']])
    table.add_row(['Dedicated', load_balancer['dedicatedFlag']])
    table.add_row(['HA', load_balancer['highAvailabilityFlag']])
    table.add_row(['SSL Enabled', load_balancer['sslEnabledFlag']])
    table.add_row(['SSL Active', load_balancer['sslActiveFlag']])

    index0 = 1
    for virtual_server in load_balancer['virtualServers']:
        for group in virtual_server['serviceGroups']:
            service_group_table = formatting.KeyValueTable(['name', 'value'])

            table.add_row(['Service Group %s' % index0, service_group_table])
            index0 += 1

            service_group_table.add_row(['Guest ID',
                                         virtual_server['id']])
            service_group_table.add_row(['Port', virtual_server['port']])
            service_group_table.add_row(['Allocation',
                                         '%s %%' %
                                         virtual_server['allocation']])
            service_group_table.add_row(['Routing Type',
                                         '%s:%s' %
                                         (group['routingTypeId'],
                                          group['routingType']['name'])])
            service_group_table.add_row(['Routing Method',
                                         '%s:%s' %
                                         (group['routingMethodId'],
                                          group['routingMethod']['name'])])

            index1 = 1
            for service in group['services']:
                service_table = formatting.KeyValueTable(['name', 'value'])

                service_group_table.add_row(['Service %s' % index1,
                                             service_table])
                index1 += 1

                health_check = service['healthChecks'][0]
                service_table.add_row(['Service ID', service['id']])
                service_table.add_row(['IP Address',
                                       service['ipAddress']['ipAddress']])
                service_table.add_row(['Port', service['port']])
                service_table.add_row(['Health Check',
                                       '%s:%s' %
                                       (health_check['healthCheckTypeId'],
                                        health_check['type']['name'])])
                service_table.add_row(
                    ['Weight', service['groupReferences'][0]['weight']])
                service_table.add_row(['Enabled', service['enabled']])
                service_table.add_row(['Status', service['status']])

    env.fout(table)
