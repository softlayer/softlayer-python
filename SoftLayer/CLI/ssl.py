#!/usr/bin/env python
from SoftLayer.CLI import CLIRunnable, no_going_back, Table
from SoftLayer.SSL import SSLManager

__doc__ = "Manages SSL"


def add_certificate_arguments(parser):
    parser.add_argument('--icc')
    parser.add_argument('--csr')
    parser.add_argument('--notes')


class ListCerts(CLIRunnable):
    """ list ssl certificates """
    action = 'list'

    @staticmethod
    def add_additional_args(parser):
        parser.add_argument(
            '--status',
            help='Show certificates with specific status',
            choices=[
                'valid', 'expired', 'all'
            ],
            default='all')
        parser.add_argument(
            '--sortby', choices=[
                'id', 'common_name', 'days_until_expire', 'notes'
            ],
            default='id')

    @staticmethod
    def execute(client, args):
        manager = SSLManager(client)

        certificates = manager.list_certs(args.status)

        t = Table(
            ['id', 'common_name', 'days_until_expire', 'notes']
        )
        for certificate in certificates:
            t.add_row([
                certificate['id'],
                certificate['commonName'],
                certificate['validityDays'],
                certificate.get('notes', None)
            ])
            t.sortby = args.sortby
            print t


class AddCertificate(CLIRunnable):
    """add ssl crt"""
    action = 'create'

    @staticmethod
    def add_additional_args(parser):
        parser.add_argument('crt')
        parser.add_argument('key')
        return add_certificate_arguments(parser)

    @staticmethod
    def execute(client, args):
        template = {
            'intermediateCertificate': '',
            'certificateSigningRequest': '',
            'notes': args.notes
        }
        try:
            template['certificate'] = open(args.crt).read()
            template['privateKey'] = open(args.key).read()
            if args.csr:
                template['intermediateCertificate'] = open(args.csr).read()

            if args.icc:
                template['certificateSigningRequest'] = open(args.icc).read()

        except IOError:
            raise ValueError("File does not exist")
            exit(1)

        manager = SSLManager(client)
        cert = manager.add_certificate(template)
        print("Created certificate:", cert['commonName'])
        print("Created certificate:", cert['name'])


class EditCertificate(CLIRunnable):
    """edit ssl crt"""
    action = 'edit'

    @staticmethod
    def add_additional_args(parser):
        parser.add_argument('id', help='id of certificate to modify')
        parser.add_argument('--crt')
        parser.add_argument('--key')
        add_certificate_arguments(parser)

    @staticmethod
    def execute(client, args):
        template = {'id': args.id}
        if args.crt:
            template['certificate'] = open(args.certificate).read()
        if args.key:
            template['privateKey'] = open(args.key).read()
        if args.csr:
            template['intermediateCertificate'] = open(args.csr).read()
        if args.icc:
            template['certificateSigningRequest'] = open(args.icc).read()
        if args.notes:
            template['notes'] = args.notes

        manager = SSLManager(client)
        manager.edit_certificate(template)


class RemoveCertificate(CLIRunnable):
    """remove ssl crt"""
    action = 'remove'

    @staticmethod
    def add_additional_args(parser):
        parser.add_argument('id')

    @staticmethod
    def execute(client, args):
        manager = SSLManager(client)
        if args.really or no_going_back('yes'):
            manager.remove_certificate(args.id)
            print("Deleted certificate:", args.id)
        else:
            print("Aborted.")


class DownloadCertificate(CLIRunnable):
    """download certificate & key file"""
    action = 'download'

    @staticmethod
    def add_additional_args(parser):
        parser.add_argument('id')

    @staticmethod
    def execute(client, args):
        def write_cert(filename, content):
            try:
                fo = open(filename, 'w')
                fo.write(content)
            finally:
                fo.close()

        manager = SSLManager(client)
        certificate = manager.get_certificate(args.id)

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
