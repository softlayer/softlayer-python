"""
usage: sl dedicated [<command>] [<args>...] [options]
       sl ssl [-h | --help]

Manage Dedicated

The available commands are:
  list      List dedicated certificates
"""
from SoftLayer.CLI.helpers import CLIRunnable, Table
from SoftLayer.dedicated import DedicatedManager
from pprint import pprint as pp


class ListServers(CLIRunnable):
    """
usage: sl dedicated list

List dedicated servers on the acount
"""
    action = 'list'

    @staticmethod
    def execute(client, args):
        manager = DedicatedManager(client)

        servers = manager.list_servers()
        t = Table(['id', 'hostname', 'domain'])
        for server in servers:
            t.add_row([
                server['id'],
                server['hostname'],
                server['domain']
            ])

        pp(t)
        return t
