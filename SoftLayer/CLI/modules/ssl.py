"""
usage: sl ssl [<command>] [<args>...] [options]
       sl ssl [-h | --help]

Manage SSL

The available commands are:
  add       Add ssl certificate
  download  Download certificate & key file
  edit      Edit ssl certificate
  list      List ssl certificates
  remove    Remove ssl certificate
"""
# :license: MIT, see LICENSE for more details.

from SoftLayer.CLI.helpers import CLIRunnable, no_going_back, Table, CLIAbort
from SoftLayer.CLI.helpers import blank
from SoftLayer import SSLManager


class ListCerts(CLIRunnable):
    """
usage: sl ssl list [options]

List SSL certificates on the acount

Options:
  --status=STATUS  Show certificates with this status. [Default: all]
                     [Options: valid, expired, all]
  --sortby=SORTBY  Sort by this value. [Default: id]
                     [Options: id, common_name, days_until_expire, notes]
"""
    action = 'list'

    def execute(self, args):
        manager = SSLManager(self.client)

        certificates = manager.list_certs(args['--status'])

        table = Table(['id', 'common_name', 'days_until_expire', 'notes'])
        for certificate in certificates:
            table.add_row([
                certificate['id'],
                certificate['commonName'],
                certificate['validityDays'],
                certificate.get('notes', blank())
            ])
        table.sortby = args['--sortby']
        return table


class AddCertificate(CLIRunnable):
    """
usage: sl ssl add --crt=FILE --key=FILE [options]

Add and upload SSL certificate details

Options:
  --crt=FILE     Certificate file
  --csr=FILE     Certificate Signing Request file
  --icc=FILE     Intermediate Certificate file
  --key=FILE     Private Key file
  --notes=NOTES  Additional notes
"""
    action = 'add'

    def execute(self, args):
        template = {
            'intermediateCertificate': '',
            'certificateSigningRequest': '',
            'notes': args['--notes'],
        }
        try:
            template['certificate'] = open(args['--crt']).read()
            template['privateKey'] = open(args['--key']).read()
            if args['--csr']:
                template['certificateSigningRequest'] = \
                    open(args['--csr']).read()

            if args['--icc']:
                template['intermediateCertificate'] = \
                    open(args['--icc']).read()

        except IOError:
            raise CLIAbort("File does not exist")

        manager = SSLManager(self.client)
        manager.add_certificate(template)


class EditCertificate(CLIRunnable):
    """
usage: sl ssl edit <id> [options]

Edit SSL certificate

Options:
  --crt=FILE     Certificate file
  --csr=FILE     Certificate Signing Request file
  --icc=FILE     Intermediate Certificate file
  --key=FILE     Private Key file
  --notes=NOTES  Additional notes
"""
    action = 'edit'

    def execute(self, args):
        template = {'id': args['<id>']}
        if args['--crt']:
            template['certificate'] = open(args['--crt']).read()
        if args['--key']:
            template['privateKey'] = open(args['--key']).read()
        if args['--csr']:
            template['certificateSigningRequest'] = open(args['--csr']).read()
        if args['--icc']:
            template['intermediateCertificate'] = open(args['--icc']).read()
        if args['--notes']:
            template['notes'] = args['--notes']

        manager = SSLManager(self.client)
        manager.edit_certificate(template)


class RemoveCertificate(CLIRunnable):
    """
usage: sl ssl remove <id> [options]

Remove SSL certificate
"""
    action = 'remove'
    options = ['confirm']

    def execute(self, args):
        manager = SSLManager(self.client)
        if args['--really'] or no_going_back('yes'):
            manager.remove_certificate(args['<id>'])
        raise CLIAbort("Aborted.")


class DownloadCertificate(CLIRunnable):
    """
usage: sl ssl download <id> [options]

Download SSL certificate and key file
"""
    action = 'download'

    def execute(self, args):
        def write_cert(filename, content):
            """ Writes certificate body to the given file path """
            with open(filename, 'w') as cert_file:
                cert_file.write(content)

        manager = SSLManager(self.client)
        certificate = manager.get_certificate(args['<id>'])

        write_cert(
            certificate['commonName'] + '.crt', certificate['certificate'])
        write_cert(
            certificate['commonName'] + '.key', certificate['privateKey'])
        if 'intermediateCertificate' in certificate:
            write_cert(
                certificate['commonName'] + '.icc',
                certificate['intermediateCertificate'])
        if 'certificateSigningRequest' in certificate:
            write_cert(
                certificate['commonName'] + '.csr',
                certificate['certificateSigningRequest'])
