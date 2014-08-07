"""
usage: sl sshkey [<command>] [<args>...] [options]

Manage SSH keys

The available commands are:
  add     Add a new SSH key to your account
  remove  Removes an SSH key
  edit    Edits information about the SSH key
  list    Display a list of SSH keys on your account
  print   Prints out an SSH key
"""
# :license: MIT, see LICENSE for more details.

from os import path

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers


class AddSshKey(environment.CLIRunnable):
    """
usage: sl sshkey add <label> (--file=FILE | --key=KEY ) [options]

Add a new SSH key to your account

Required:
  <label>                  The label for your SSH key. will appear in various
                             interfaces to help you easily identify this key.
                             You can enclose multiple words in quotation marks
                             "like this" if desired
  -f FILE, --file=FILE     The id_rsa.pub file to import for this key. Mutually
                             exclusive with --key
  -k KEY, --key=KEY        The actual SSH key. Mutually exclusive with --file.
                             Should be enclosed within quotation marks

Optional:
  -n NOTES, --notes=NOTES  Any notes you want to add to the SSH key
"""
    action = 'add'

    def execute(self, args):
        if args.get('--key'):
            key = args['--key']
        else:
            key_file = open(path.expanduser(args['--file']), 'rU')
            key = key_file.read().strip()
            key_file.close()

        mgr = SoftLayer.SshKeyManager(self.client)
        result = mgr.add_key(key, args['<label>'], args.get('--notes'))

        return "SSH key added: %s" % result.get('fingerprint')


class RemoveSshKey(environment.CLIRunnable):
    """
usage: sl sshkey remove <identifier> [options]

Permanently removes an SSH key from your account

Required:
  <identifier>   The ID or label for the SSH key to be removed

"""

    action = 'remove'
    options = ['confirm']

    def execute(self, args):
        mgr = SoftLayer.SshKeyManager(self.client)

        key_id = helpers.resolve_id(mgr.resolve_ids,
                                    args.get('<identifier>'),
                                    'SshKey')
        if args['--really'] or formatting.no_going_back(key_id):
            mgr.delete_key(key_id)
        else:
            raise exceptions.CLIAbort('Aborted')


class EditSshKey(environment.CLIRunnable):
    """
usage: sl sshkey edit <identifier> [options]

Options:
  -l, --label=LABEL The new label for the key
  -n, --notes=NOTES New notes for the key
"""

    action = 'edit'

    def execute(self, args):
        mgr = SoftLayer.SshKeyManager(self.client)

        key_id = helpers.resolve_id(mgr.resolve_ids,
                                    args.get('<identifier>'),
                                    'SshKey')

        if not mgr.edit_key(key_id,
                            label=args['--label'],
                            notes=args['--notes']):
            raise exceptions.CLIAbort('Failed to edit SSH key')


class ListSshKey(environment.CLIRunnable):
    """
usage: sl sshkey list [options]

Display a list of SSH keys on your account

Options:
  --sortby=ARG  Column to sort by. options: label, fingerprint, notes
"""
    action = 'list'

    def execute(self, args):
        mgr = SoftLayer.SshKeyManager(self.client)
        keys = mgr.list_keys()

        table = formatting.Table(['id', 'label', 'fingerprint', 'notes'])

        for key in keys:
            table.add_row([key['id'],
                           key.get('label'),
                           key.get('fingerprint'),
                           key.get('notes', '-')])

        return table


class PrintSshKey(environment.CLIRunnable):
    """
usage: sl sshkey print <identifier> [--file=FILE]

Prints out an SSH key to the screen

Options:
  -f FILE, --file=FILE  If specified, the public SSH key will be written to
                          this file
"""
    action = 'print'

    def execute(self, args):
        mgr = SoftLayer.SshKeyManager(self.client)

        key_id = helpers.resolve_id(mgr.resolve_ids,
                                    args.get('<identifier>'),
                                    'SshKey')

        key = mgr.get_key(key_id)

        if args.get('--file'):
            with open(path.expanduser(args['--file']), 'w') as pub_file:
                pub_file.write(key['key'])

        table = formatting.KeyValueTable(['Name', 'Value'])
        table.add_row(['id', key['id']])
        table.add_row(['label', key.get('label')])
        table.add_row(['notes', key.get('notes', '-')])
        return table
