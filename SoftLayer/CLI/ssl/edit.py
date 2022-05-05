"""Edit SSL certificate."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
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
    with open(crt, encoding="utf-8") as file_crt:
        if crt:
            template['certificate'] = file_crt.read()
    with open(key, encoding="utf-8") as file_key:
        if key:
            template['privateKey'] = file_key.read()
    with open(csr, encoding="utf-8") as file_csr:
        if csr:
            template['certificateSigningRequest'] = file_csr.read()
    with open(icc, encoding="utf-8") as file_icc:
        if icc:
            template['intermediateCertificate'] = file_icc.read()
    if notes:
        template['notes'] = notes

    manager = SoftLayer.SSLManager(env.client)
    manager.edit_certificate(template)
