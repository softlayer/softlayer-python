"""Add and upload SSL certificate details."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment


@click.command()
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
    template['certificate'] = open(crt).read()
    template['privateKey'] = open(key).read()
    if csr:
        body = open(csr).read()
        template['certificateSigningRequest'] = body

    if icc:
        body = open(icc).read()
        template['intermediateCertificate'] = body

    manager = SoftLayer.SSLManager(env.client)
    manager.add_certificate(template)
