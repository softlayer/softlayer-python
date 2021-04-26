"""Import an image."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting


@click.command()
@click.argument('name')
@click.argument('uri')
@click.option('--note',
              default="",
              help="The note to be applied to the imported template")
@click.option('--os-code',
              help="The referenceCode of the operating system software"
                   " description for the imported VHD, ISO, or RAW image")
@click.option('--ibm-api-key',
              default=None,
              help="The IBM Cloud API Key with access to IBM Cloud Object "
                   "Storage instance and IBM KeyProtect instance. For help "
                   "creating this key see https://cloud.ibm.com/docs/"
                   "cloud-object-storage?topic=cloud-object-storage"
                   "-iam-overview#iam-overview-service-id-api-key")
@click.option('--root-key-crn',
              default=None,
              help="CRN of the root key in your KMS instance")
@click.option('--wrapped-dek',
              default=None,
              help="Wrapped Data Encryption Key provided by IBM KeyProtect. "
                   "For more info see "
                   "https://cloud.ibm.com/docs/key-protect?topic=key-protect-wrap-keys")
@click.option('--cloud-init',
              is_flag=True,
              help="Specifies if image is cloud-init")
@click.option('--byol',
              is_flag=True,
              help="Specifies if image is bring your own license")
@click.option('--is-encrypted',
              is_flag=True,
              help="Specifies if image is encrypted")
@environment.pass_env
def cli(env, name, note, os_code, uri, ibm_api_key, root_key_crn, wrapped_dek,
        cloud_init, byol, is_encrypted):
    """Import an image.

    The URI for an object storage object (.vhd/.iso file) of the format:
    swift://<objectStorageAccount>@<cluster>/<container>/<objectPath>
    or cos://<regionName>/<bucketName>/<objectPath> if using IBM Cloud
    Object Storage
    """

    image_mgr = SoftLayer.ImageManager(env.client)
    result = image_mgr.import_image_from_uri(
        name=name,
        note=note,
        os_code=os_code,
        uri=uri,
        ibm_api_key=ibm_api_key,
        root_key_crn=root_key_crn,
        wrapped_dek=wrapped_dek,
        cloud_init=cloud_init,
        byol=byol,
        is_encrypted=is_encrypted
    )

    if not result:
        raise exceptions.CLIAbort("Failed to import Image")

    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'
    table.add_row(['name', result['name']])
    table.add_row(['id', result['id']])
    table.add_row(['created', result['createDate']])
    table.add_row(['guid', result['globalIdentifier']])
    env.fout(table)
