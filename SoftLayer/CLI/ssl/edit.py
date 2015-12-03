"""Edit SSL certificate."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment


@click.command()
@click.argument('identifier')
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
def cli(env, identifier, crt, csr, icc, key, notes):
    """Edit SSL certificate."""
    template = {'id': identifier}
    if crt:
        template['certificate'] = open(crt).read()
    if key:
        template['privateKey'] = open(key).read()
    if csr:
        template['certificateSigningRequest'] = open(csr).read()
    if icc:
        template['intermediateCertificate'] = open(icc).read()
    if notes:
        template['notes'] = notes

    manager = SoftLayer.SSLManager(env.client)
    manager.edit_certificate(template)
