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
    table.add_row(['General properties', '----------'])
    table.add_row([' ID', 'local:%s' % load_balancer['id']])
    table.add_row([' IP Address', load_balancer['ipAddress']['ipAddress']])
    name = load_balancer['loadBalancerHardware'][0]['datacenter']['name']
    table.add_row([' Datacenter', name])
    table.add_row([' Connections limit', load_balancer['connectionLimit']])
    table.add_row([' Dedicated', load_balancer['dedicatedFlag']])
    table.add_row([' HA', load_balancer['highAvailabilityFlag']])
    table.add_row([' SSL Enabled', load_balancer['sslEnabledFlag']])
    table.add_row([' SSL Active', load_balancer['sslActiveFlag']])
    index0 = 1
    for virtual_server in load_balancer['virtualServers']:
        table.add_row(['Service group %s' % index0,
                       '**************'])
        index0 += 1
        table2 = formatting.Table(['Service group ID',
                                   'Port',
                                   'Allocation',
                                   'Routing type',
                                   'Routing Method'])

        for group in virtual_server['serviceGroups']:
            table2.add_row([
                '%s:%s' % (load_balancer['id'], virtual_server['id']),
                virtual_server['port'],
                '%s %%' % virtual_server['allocation'],
                '%s:%s' % (group['routingTypeId'],
                           group['routingType']['name']),
                '%s:%s' % (group['routingMethodId'],
                           group['routingMethod']['name'])
            ])

            table.add_row([' Group Properties', table2])

            table3 = formatting.Table(['Service_ID',
                                       'IP Address',
                                       'Port',
                                       'Health Check',
                                       'Weight',
                                       'Enabled',
                                       'Status'])
            service_exist = False
            for service in group['services']:
                service_exist = True
                health_check = service['healthChecks'][0]
                table3.add_row([
                    '%s:%s' % (load_balancer['id'], service['id']),
                    service['ipAddress']['ipAddress'],
                    service['port'],
                    '%s:%s' % (health_check['healthCheckTypeId'],
                               health_check['type']['name']),
                    service['groupReferences'][0]['weight'],
                    service['enabled'],
                    service['status']
                ])
            if service_exist:
                table.add_row([' Services', table3])
            else:
                table.add_row([' Services', 'None'])

    env.fout(table)
