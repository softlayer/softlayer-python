"""
usage: sl cdn [<command>] [<args>...] [options]

Manage CDN accounts and configuration

The available commands are:
  detail         Show details for a CDN account
  list           List CDN accounts
  load           Cache one or more files on all edge nodes
  origin-add     Add an origin pull mapping
  origin-list    Show origin pull mappings on a CDN account
  origin-remove  Remove an origin pull mapping
  purge          Purge one or more cached files from all edge nodes
"""
# :license: MIT, see LICENSE for more details.

from SoftLayer.CLI import CLIRunnable, Table, KeyValueTable, blank
from SoftLayer.managers.cdn import CDNManager


class ListAccounts(CLIRunnable):
    """
usage: sl cdn list [options]

List all CDN accounts

Options:
  --sortby=SORTBY  Sort by this value. [Default: id]
                     [Options: id, account_name, type, created, notes]
"""
    action = 'list'

    def execute(self, args):
        manager = CDNManager(self.client)
        accounts = manager.list_accounts()

        table = Table(['id', 'account_name', 'type', 'created', 'notes'])
        for account in accounts:
            table.add_row([
                account['id'],
                account['cdnAccountName'],
                account['cdnSolutionName'],
                account['createDate'],
                account.get('cdnAccountNote', blank())
            ])

        table.sortby = args['--sortby']
        return table


class DetailAccount(CLIRunnable):
    """
usage: sl cdn detail <account> [options]

Show CDN account details
"""
    action = 'detail'

    def execute(self, args):
        manager = CDNManager(self.client)
        account = manager.get_account(args.get('<account>'))

        table = KeyValueTable(['Name', 'Value'])
        table.align['Name'] = 'r'
        table.align['Value'] = 'l'

        table.add_row(['id', account['id']])
        table.add_row(['account_name', account['cdnAccountName']])
        table.add_row(['type', account['cdnSolutionName']])
        table.add_row(['status', account['status']['name']])
        table.add_row(['created', account['createDate']])
        table.add_row(['notes', account.get('cdnAccountNote', blank())])

        return table


class LoadContent(CLIRunnable):
    """
usage: sl cdn load <account> <content_url>... [options]

Cache one or more files on all edge nodes

Required:
  account      The CDN account ID to cache content in
  content_url  The CDN URL(s) or CDN CNAME-based URL(s) for the content
                 you wish to cache (can be repeated)
"""
    action = 'load'
    required_params = ['account', 'content_url']

    def execute(self, args):
        manager = CDNManager(self.client)
        manager.load_content(args.get('<account>'), args.get('<content_url>'))


class PurgeContent(CLIRunnable):
    """
usage: sl cdn purge <account> <content_url>... [options]

Purge one or more cached files from all edge nodes

Required:
  account      The CDN account ID to purge content from
  content_url  The CDN URL(s) or CDN CNAME-based URL(s) for the content
                 you wish to cache (can be repeated)
"""
    action = 'purge'
    required_params = ['account', 'content_url']

    def execute(self, args):
        manager = CDNManager(self.client)
        manager.purge_content(args.get('<account>'),
                              args.get('<content_url>'))


class ListOrigins(CLIRunnable):
    """
usage: sl cdn origin-list <account> [options]

List origin pull mappings associated with a CDN account.
"""
    action = 'origin-list'

    def execute(self, args):
        manager = CDNManager(self.client)
        origins = manager.get_origins(args.get('<account>'))

        table = Table(['id', 'media_type', 'cname', 'origin_url'])

        for origin in origins:
            table.add_row([origin['id'],
                           origin['mediaType'],
                           origin.get('cname', blank()),
                           origin['originUrl']])

        return table


class AddOrigin(CLIRunnable):
    """
usage: sl cdn origin-add <account> <url> [options]

Create an origin pull mapping on a CDN account

Required:
  account  The CDN account ID to create a mapping on
  url      A full URL where content should be pulled from by
             CDN edge nodes

Options:
  --type=TYPE    The media type for this mapping (http, flash, wm, ...)
                   (default: http)
  --cname=CNAME  An optional CNAME to attach to the mapping
"""
    action = 'origin-add'
    required_params = ['account', 'url']

    def execute(self, args):
        manager = CDNManager(self.client)
        media_type = args.get('--type') or 'http'

        manager.add_origin(args.get('<account>'), media_type,
                           args.get('<url>'), args.get('--cname', None))


class RemoveOrigin(CLIRunnable):
    """
usage: sl cdn origin-remove <account> <origin_id> [options]

Remove an origin pull mapping from a CDN account

Required:
  account    The CDN account ID to remove a mapping from
  origin_id  The origin mapping ID to remove
"""
    action = 'origin-remove'
    required_params = ['account', 'origin_id']

    def execute(self, args):
        manager = CDNManager(self.client)
        manager.remove_origin(args.get('<account>'),
                              args.get('<origin_id>'))
