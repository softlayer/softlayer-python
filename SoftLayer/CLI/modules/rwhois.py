"""
usage: sl rwhois [<command>] [<args>...] [options]

Manage the RWhoIs information on the account.

The available commands are:
  edit  Edit the RWhois data on the account
  show  Show the RWhois data on the account
"""
# :license: MIT, see LICENSE for more details.

from SoftLayer import NetworkManager
from SoftLayer.CLI import CLIRunnable, KeyValueTable
from SoftLayer.CLI.helpers import CLIAbort


class RWhoisEdit(CLIRunnable):
    """
usage: sl rwhois edit [options]

Updates the RWhois information on your account. Only the fields you
specify will be changed. To clear a value, specify an empty string like: ""

Options:
  --abuse=EMAIL      Set the abuse email
  --address1=ADDR    Update the address 1 field
  --address2=ADDR    Update the address 2 field
  --city=CITY        Set the city information
  --company=NAME     Set the company name
  --country=COUNTRY  Set the country information. Use the two-letter
                       abbreviation.
  --firstname=NAME   Update the first name field
  --lastname=NAME    Update the last name field
  --postal=CODE      Set the postal code field
  --private          Flags the address as a private residence.
  --public           Flags the address as a public residence.
  --state=STATE      Set the state information. Use the two-letter
                       abbreviation.
"""
    action = 'edit'

    def execute(self, args):
        mgr = NetworkManager(self.client)

        update = {
            'abuse_email': args.get('--abuse'),
            'address1': args.get('--address1'),
            'address2': args.get('--address2'),
            'company_name': args.get('--company'),
            'city': args.get('--city'),
            'country': args.get('--country'),
            'first_name': args.get('--firstname'),
            'last_name': args.get('--lastname'),
            'postal_code': args.get('--postal'),
            'state': args.get('--state')
        }

        if args.get('--private'):
            update['private_residence'] = False
        elif args.get('--public'):
            update['private_residence'] = True

        check = [x for x in update.values() if x is not None]
        if not check:
            raise CLIAbort("You must specify at least one field to update.")

        mgr.edit_rwhois(**update)  # pylint: disable=W0142


class RWhoisShow(CLIRunnable):
    """
usage: sl rwhois show [options]

Display the RWhois information for your account.
"""
    action = 'show'

    def execute(self, args):
        mgr = NetworkManager(self.client)
        result = mgr.get_rwhois()

        table = KeyValueTable(['Name', 'Value'])
        table.align['Name'] = 'r'
        table.align['Value'] = 'l'
        table.add_row(['Name', result['firstName'] + ' ' + result['lastName']])
        table.add_row(['Company', result['companyName']])
        table.add_row(['Abuse Email', result['abuseEmail']])
        table.add_row(['Address 1', result['address1']])
        if result.get('address2'):
            table.add_row(['Address 2', result['address2']])
        table.add_row(['City', result['city']])
        table.add_row(['State', result.get('state', '-')])
        table.add_row(['Postal Code', result.get('postalCode', '-')])
        table.add_row(['Country', result['country']])

        return table
