"""Add and upload SSL certificate details."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.option('--crt',
              type=click.Path(exists=True),
              help="Certificate file")
@click.option('--csr',
              type=click.Path(exists=True),
              help="Certificate Signing Request file")
@click.option('--icc',
              type=click.Path(exists=True),
              help="Intermediate Certificate file")
@click.option('--key', type=click.Path(exists=True), help="Private Key file")
@click.option('--notes', help="Additional notes")
@environment.pass_env
def cli(env, crt, csr, icc, key, notes):
    """Add and upload SSL certificate details."""

    template = {
        'intermediateCertificate': '',
        'certificateSigningRequest': '',
        'notes': notes,
    }
    with open(crt, encoding="utf-8") as file_crt:
        template['certificate'] = file_crt.read()
    with open(key, encoding="utf-8") as file_key:
        template['privateKey'] = file_key.read()
    with open(csr, encoding="utf-8") as file_csr:
        if csr:
            body = file_csr.read()
            template['certificateSigningRequest'] = body

    with open(icc, encoding="utf-8") as file_icc:
        if icc:
            body = file_icc.read()
            template['intermediateCertificate'] = body

    manager = SoftLayer.SSLManager(env.client)
    manager.add_certificate(template)
