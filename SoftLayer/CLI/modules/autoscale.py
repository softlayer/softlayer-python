"""
usage: sl autoscale [<command>] [<args>...] [options]

Manage compute images

The available commands are:
  list    List autoscale groups
"""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


class ListGroups(environment.CLIRunnable):
    """
usage: sl autoscale list [options]

List autoscale groups
"""
    action = 'list'

    def execute(self, args):
        autoscale_mgr = SoftLayer.AutoscaleManager(self.client)


        mask="virtualGuestAssetCount"
        groups = autoscale_mgr.list_groups(mask=mask)
        

        table = formatting.Table(['id',
                                  'name',
                                  'status',
                                  'min members',
                                  'max members',
                                  'desired members',
                                  'current'])
        
        for group in groups:
            table.add_row([
                group['id'],
                group['name'].strip(),
                group['status']['name'],
                group['minimumMemberCount'],
                group['maximumMemberCount'],
                group['desiredMemberCount'],
                group['virtualGuestAssetCount']
            ])

        return table

class DetailGroup(environment.CLIRunnable):
    """
usage: sl autoscale detail <identifier> [options]

Get details for an autoscale group
"""
    action = 'detail'

    def execute(self, args):
        autoscale_mgr = SoftLayer.AutoscaleManager(self.client)

        group_id = helpers.resolve_id(autoscale_mgr.resolve_ids,
                                      args.get('<identifier>'),
                                      'autoscale')

        group = autoscale_mgr.get_group(group_id)
        
        
        pad=0
        table = formatting.Table(['Name', 'Value'])
        table.align['Name'] = 'l'
        table.align['Value'] = 'l'
        table.add_row(['id',group['id']])
        table.add_row(['name',group['name']])
        table.add_row(['status',group['status']['name']])
        table.add_row(['region group',group['regionalGroup']['name']])
        table.add_row(['min members',group['minimumMemberCount']])
        table.add_row(['max members',group['maximumMemberCount']])
        table.add_row(['desired members',group['desiredMemberCount']])
        
        table.add_row(['vs template',''])
        pad=pad+3
        if 'datacenter' in group['virtualGuestMemberTemplate']:
            datacenter=group['virtualGuestMemberTemplate']['datacenter']['name']
        else:
            datacenter='Any'
        table.add_row([' '*pad+'datacenter',datacenter])
        table.add_row([' '*pad+'billing','hourly' if group['virtualGuestMemberTemplate']['hourlyBillingFlag'] == True else 'monthly'])
        table.add_row([' '*pad+'hostname prefix',group['virtualGuestMemberTemplate']['hostname']])
        table.add_row([' '*pad+'domain',group['virtualGuestMemberTemplate']['domain']])
        table.add_row([' '*pad+'os',group['virtualGuestMemberTemplate']['operatingSystemReferenceCode']])
        table.add_row([' '*pad+'cores',group['virtualGuestMemberTemplate']['startCpus']])
        table.add_row([' '*pad+'memory',group['virtualGuestMemberTemplate']['maxMemory']])
        table.add_row([' '*pad+'networks','private' if group['virtualGuestMemberTemplate']['privateNetworkOnlyFlag'] == True else 'private,public'])
        pad=pad-3
        
        vscols = ['id','datacenter','hostname','backend_ip']
        if group['virtualGuestMemberTemplate']['privateNetworkOnlyFlag'] == True:
            vscols.append('primary_ip')
        vstable = formatting.Table(vscols)
        
        table.add_row(['cooldown',group['cooldown']])

        return table
