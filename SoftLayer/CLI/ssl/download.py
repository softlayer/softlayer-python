"""Download SSL certificate and key file."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """Download SSL certificate and key file."""

    manager = SoftLayer.SSLManager(env.client)
    certificate = manager.get_certificate(identifier)

    write_cert(certificate['commonName'] + '.crt', certificate['certificate'])
    write_cert(certificate['commonName'] + '.key', certificate['privateKey'])

    if 'intermediateCertificate' in certificate:
        write_cert(certificate['commonName'] + '.icc',
                   certificate['intermediateCertificate'])

    if 'certificateSigningRequest' in certificate:
        write_cert(certificate['commonName'] + '.csr',
                   certificate['certificateSigningRequest'])


def write_cert(filename, content):
    """Writes certificate body to the given file path."""
    with open(filename, 'w', encoding="utf-8") as cert_file:
        cert_file.write(content)
