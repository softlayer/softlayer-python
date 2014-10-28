"""
usage: sl monitor [<command>] [<args>...] [options]

Manage Monitoring.

The available commands are:
    status  Show basic monitoring status of servers

"""

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer import utils


from pprint import pprint as pp
from datetime import date

class MonitorStatus(environment.CLIRunnable):
    """
usage: sl monitor status [options]

Unless specified, shows status of all servers.

Options:
    --hardware  only show hardware servers
    --virtual   only show virtual servers

    """
    action = 'status'
    def execute(self, args):
        hardware = args.get('--hardware')
        virtual = args.get('--virtual')

        table = formatting.Table([
            'id', 'datacenter', 'FQDN', 'public ip',
            'status', 'last checked at'
            ])

        manager = SoftLayer.MonitoringManager(self.client)
        results = manager.list_hardware_status()
        for server in results:
            server = utils.NestedDict(server)
            res = server['networkMonitors'][0]['lastResult']['responseStatus']
            date = server['networkMonitors'][0]['lastResult']['finishTime']
            status = '\033[35mUNKNOWN\033[0m'
            if  res == 0:
                status = '\033[31mDOWN\033[0m'
            elif res == 1:
                status = '\033[93mWARNING\033[0m'
            elif res == 2:
                status = '\033[32mOK\033[0m'

            table.add_row([
                server['id'],
                server['datacenter']['name'] or formatting.blank(),
                server['fullyQualifiedDomainName'],
                server['primaryIpAddress'] or formatting.blank(),
                status,
                date
                ])

        return table