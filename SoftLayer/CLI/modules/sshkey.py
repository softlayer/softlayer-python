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
# :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
# :license: MIT, see LICENSE for more details.

from os.path import expanduser

from SoftLayer import SshKeyManager
from SoftLayer.CLI import CLIRunnable, Table, no_going_back
from SoftLayer.CLI.helpers import CLIAbort, resolve_id, KeyValueTable


class AddSshKey(CLIRunnable):
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

    @staticmethod
    def execute(client, args):
        if args.get('--key'):
            key = args['--key']
        else:
            f = open(expanduser(args['--file']), 'rU')
            key = f.read().strip()
            f.close()

        mgr = SshKeyManager(client)
        result = mgr.add_key(key, args['<label>'], args.get('--notes'))

        if type(result) is dict and result.get('fingerprint'):
            return "SSH key added."


class RemoveSshKey(CLIRunnable):
    """
usage: sl sshkey remove <identifier> [options]

Permanently removes an SSH key from your account

Required:
  <identifier>   The ID or label for the SSH key to be removed

"""

    action = 'remove'
    options = ['confirm']

    @staticmethod
    def execute(client, args):
        mgr = SshKeyManager(client)

        key_id = resolve_id(mgr.resolve_ids,
                            args.get('<identifier>'), 'SshKey')
        if args['--really'] or no_going_back(key_id):
            mgr.delete_key(key_id)
        else:
            CLIAbort('Aborted')


class EditSshKey(CLIRunnable):
    """
usage: sl sshkey edit <identifier> [options]

Options:
  -l, --label=LABEL The new label for the key
  -n, --notes=NOTES New notes for the key
"""

    action = 'edit'

    @staticmethod
    def execute(client, args):
        mgr = SshKeyManager(client)

        key_id = resolve_id(mgr.resolve_ids,
                            args.get('<identifier>'), 'SshKey')

        data = {}
        if args.get('--label'):
            data['label'] = args['--label']
        if args.get('--notes'):
            data['notes'] = args['--notes']

        if not mgr.edit_key(key_id, **data):
            raise CLIAbort('Failed to edit SSH key')


class ListSshKey(CLIRunnable):
    """
usage: sl sshkey list [options]

Display a list of SSH keys on your account

Options:
  --sortby=ARG  Column to sort by. options: datacenter, vlans, subnets, IPs,
                  networking, hardware, ccis, firewall
"""
    action = 'list'

    @staticmethod
    def execute(client, args):
        mgr = SshKeyManager(client)
        keys = mgr.list_keys()

        t = Table(['id', 'label', 'fingerprint', 'notes'])

        for key in keys:
            t.add_row([key['id'], key['label'], key['fingerprint'],
                       key.get('notes', '-')])

        return t


class PrintSshKey(CLIRunnable):
    """
usage: sl sshkey print <identifier> [--file=FILE]

Prints out an SSH key to the screen

Options:
  -f FILE, --file=FILE  If specified, the public SSH key will be written to
                          this file
"""
    action = 'print'

    @staticmethod
    def execute(client, args):
        mgr = SshKeyManager(client)

        key_id = resolve_id(mgr.resolve_ids,
                            args.get('<identifier>'), 'SshKey')

        key = mgr.get_key(key_id)

        if args.get('--file'):
            f = open(expanduser(args['--file']), 'w')
            f.write(key['key'])
            f.close()

        t = KeyValueTable(['Name', 'Value'])
        t.add_row(['id', key['id']])
        t.add_row(['label', key['label']])
        t.add_row(['notes', key.get('notes', '-')])
        return t
