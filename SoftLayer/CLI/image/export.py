"""Export an image."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import helpers


@click.command()
@click.argument('identifier')
@click.argument('uri')
@click.option('--ibm-api-key',
              default=None,
              help="The IBM Cloud API Key with access to IBM Cloud Object "
                   "Storage instance. For help creating this key see "
                   "https://console.bluemix.net/docs/services/cloud-object-"
                   "storage/iam/users-serviceids.html#serviceidapikeys")
@environment.pass_env
def cli(env, identifier, uri, ibm_api_key):
    """Export an image to object storage.

    The URI for an object storage object (.vhd/.iso file) of the format:
    swift://<objectStorageAccount>@<cluster>/<container>/<objectPath>
    or cos://<regionName>/<bucketName>/<objectPath> if using IBM Cloud
    Object Storage
    """

    image_mgr = SoftLayer.ImageManager(env.client)
    image_id = helpers.resolve_id(image_mgr.resolve_ids, identifier, 'image')
    result = image_mgr.export_image_to_uri(image_id, uri, ibm_api_key)

    if not result:
        raise exceptions.CLIAbort("Failed to export Image")
