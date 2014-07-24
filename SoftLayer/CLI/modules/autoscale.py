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
    
    padding=0
    
    def pad_more(self):
        self.padding=self.padding+2
        
    def pad_less(self):
        self.padding=self.padding-2
        
    def pad(self,string):
        return ' '*self.padding+string

    def execute(self, args):
        autoscale_mgr = SoftLayer.AutoscaleManager(self.client)

        group_id = helpers.resolve_id(autoscale_mgr.resolve_ids,
                                      args.get('<identifier>'),
                                      'autoscale')

        group = autoscale_mgr.get_group(group_id)
        
        
        table = formatting.Table(['Name', 'Value'])
        table.align['Name'] = 'l'
        table.align['Value'] = 'l'
        table.add_row([self.pad('id'),group['id']])
        table.add_row([self.pad('name'),group['name']])
        table.add_row([self.pad('status'),group['status']['name']])
        
        table.add_row(['-------------------',''])
        table.add_row([self.pad('group membership'),""])
        self.pad_more() # group membership
        table.add_row([self.pad('region'),group['regionalGroup']['name']])
        table.add_row([self.pad('min'),group['minimumMemberCount']])
        table.add_row([self.pad('max'),group['maximumMemberCount']])
        table.add_row([self.pad('desired'),group['desiredMemberCount']])
        
        table.add_row([self.pad('vs template'),''])
        self.pad_more() # vstemplate
        if 'datacenter' in group['virtualGuestMemberTemplate']:
            datacenter=group['virtualGuestMemberTemplate']['datacenter']['name']
        else:
            datacenter='Any'
        table.add_row([self.pad('datacenter'),datacenter])
        table.add_row([self.pad('billing'),'hourly' if group['virtualGuestMemberTemplate']['hourlyBillingFlag'] == True else 'monthly'])
        table.add_row([self.pad('hostname prefix'),group['virtualGuestMemberTemplate']['hostname']])
        table.add_row([self.pad('domain'),group['virtualGuestMemberTemplate']['domain']])
        table.add_row([self.pad('os'),group['virtualGuestMemberTemplate']['operatingSystemReferenceCode']])
        table.add_row([self.pad('cores'),group['virtualGuestMemberTemplate']['startCpus']])
        table.add_row([self.pad('memory'),group['virtualGuestMemberTemplate']['maxMemory']])
        table.add_row([self.pad('networks'),'private' if group['virtualGuestMemberTemplate']['privateNetworkOnlyFlag'] == True else 'private,public'])
        self.pad_less() #vstemplae
        
        vscols = ['id','datacenter','hostname','backend_ip']
        if group['virtualGuestMemberTemplate']['privateNetworkOnlyFlag'] == False:
            vscols.append('primary_ip')
        vstable = formatting.Table(vscols)
        for vs in group['virtualGuestMembers']:
            vs = vs['virtualGuest']
            vsrow = [vs['id'],vs['datacenter']['name'],vs['hostname'],vs['primaryBackendIpAddress']]
            if group['virtualGuestMemberTemplate']['privateNetworkOnlyFlag'] == False:
                vsrow.append(vs['primaryIpAddress'])
            vstable.add_row(vsrow)
        table.add_row([self.pad('current vs'),vstable])
        self.pad_less() #group membership
        
        table.add_row(['-------------------',''])
        table.add_row([self.pad('policies'),''])
        self.pad_more() #policies
        table.add_row([self.pad('cooldown'),str(group['cooldown'])+' sec'])
        table.add_row([self.pad('terminate'),group['terminationPolicy']['name']])
        pol_count=1
        for policy in group['policies']:
            table.add_row([self.pad('policy '+str(pol_count)),'id:'+str(policy['id'])])
            self.pad_more() # policy x
            table.add_row([self.pad('name'),policy['name']])
            if policy['cooldown'] != '':
                table.add_row([self.pad('cooldown override'),str(policy['cooldown'])+' sec'])
                
            trigger_count=1
            for trigger in policy['oneTimeTriggers']:
                table.add_row([self.pad('trigger '+str(trigger_count)),'id:'+str(trigger['id'])])
                self.pad_more() # trigger x
                table.add_row([self.pad('when'),'once on '+trigger['date']])
                self.pad_less() # trigger x
                trigger_count+=1
                
            for trigger in policy['repeatingTriggers']:
                table.add_row([self.pad('trigger '+str(trigger_count)),'id:'+str(trigger['id'])])
                self.pad_more() # trigger x
                table.add_row([self.pad('when'),'on schedule '+trigger['schedule']])
                self.pad_less() # trigger x
                trigger_count+=1
            
            for trigger in policy['resourceUseTriggers']:
                table.add_row([self.pad('trigger '+str(trigger_count)),'id:'+str(trigger['id'])])
                self.pad_more() # trigger x
                
                colname='when'
                for watch in trigger['watches']:
                    table.add_row([self.pad(colname),watch['metric']+' '+watch['operator']+' '+str(watch['value'])+' for '+str(watch['period'])+' sec'])
                    colname='and'
                
                self.pad_less() # trigger x
                trigger_count+=1
                
            action=policy['scaleActions'][0]
            actionstr=''
            if action['scaleType'] == 'ABSOLUTE':
                actionstr='Scale to '+str(action['amount'])+' member(s)'
            elif action['scaleType'] == 'RELATIVE':
                actionstr='Scale by '+str(action['amount'])+' member(s)'
            else:
                actionstr='Scale by '+str(action['amount'])+'%'
            table.add_row([self.pad('action'),actionstr])
            
            self.pad_less() # policy x
            pol_count+=1
            
        self.pad_less() #policies
        
        table.add_row(['-------------------',''])
        lbtable = formatting.Table(['service group','on load balancer','connects to port on member','uses health check'])
        for lb in group['loadBalancers']:
            lbtable.add_row([lb['virtualServer']['id'],lb['virtualServer']['virtualIpAddress']['id'],
                             lb['port'],lb['healthCheck']['type']['name']])
        table.add_row([self.pad('load balancers'),lbtable])
            

        return table
