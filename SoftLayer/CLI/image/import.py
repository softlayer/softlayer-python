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
                   "creating this key see https://console.bluemix.net/docs/"
                   "services/cloud-object-storage/iam/users-serviceids.html"
                   "#serviceidapikeys")
@click.option('--root-key-id',
              default=None,
              help="ID of the root key in Key Protect")
@click.option('--wrapped-dek',
              default=None,
              help="Wrapped Data Encryption Key provided by IBM KeyProtect. "
                   "For more info see https://console.bluemix.net/docs/"
                   "services/key-protect/wrap-keys.html#wrap-keys")
@click.option('--kp-id',
              default=None,
              help="ID of the IBM Key Protect Instance")
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
def cli(env, name, note, os_code, uri, ibm_api_key, root_key_id, wrapped_dek,
        kp_id, cloud_init, byol, is_encrypted):
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
        root_key_id=root_key_id,
        wrapped_dek=wrapped_dek,
        kp_id=kp_id,
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
