"""
usage: sl cdn [<command>] [<args>...] [options]

Manage CDN

The available commands are:
  list    List CDN accounts
"""
from SoftLayer.CLI import CLIRunnable, Table
from SoftLayer.CDN import CDNManager


class ListAccounts(CLIRunnable):
    """
usage: sl cdn list [options]

List all CDN accounts

Options:
  --sortby=SORTBY  Sort by this value. [Default: id]
                     [Options: id, account_name, type, status, notes]
"""
    action = 'list'

    @staticmethod
    def execute(client, args):
        manager = CDNManager(client)
        accounts = manager.list_accounts()

        t = Table(['id', 'account_name', 'type', 'status', 'notes'])
        for account in accounts:
            t.add_row([
                account['id'],
                account['cdnAccountName'],
                account['cdnSolutionName'],
                account['status']['name'],
                account.get('cdnAccountNote', '-')
            ])

        t.sortby = args['--sortby']
        return t
