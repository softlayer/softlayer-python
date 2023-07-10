"""
    SoftLayer.image
    ~~~~~~~~~~~~~~~
    Image Manager/helpers

    :license: MIT, see LICENSE for more details.
"""

from SoftLayer import exceptions
from SoftLayer import utils

IMAGE_MASK = ('id,accountId,name,globalIdentifier,blockDevices,parentId,'
              'createDate,transaction')


class ImageManager(utils.IdentifierMixin, object):
    """Manages SoftLayer server images.

    See product information here:
    https://cloud.ibm.com/docs/image-templates

    :param SoftLayer.API.BaseClient client: the client instance
    """

    def __init__(self, client):
        self.client = client
        self.vgbdtg = self.client['Virtual_Guest_Block_Device_Template_Group']
        self.resolvers = [self._get_ids_from_name_public,
                          self._get_ids_from_name_private]

    def get_image(self, image_id, **kwargs):
        """Get details about an image.

        :param int image: The ID of the image.
        :param dict \\*\\*kwargs: response-level options (mask, limit, etc.)
        """
        if 'mask' not in kwargs:
            kwargs['mask'] = IMAGE_MASK

        return self.vgbdtg.getObject(id=image_id, **kwargs)

    def delete_image(self, image_id):
        """Deletes the specified image.

        :param int image_id: The ID of the image.
        """
        self.vgbdtg.deleteObject(id=image_id)

    def list_private_images(self, guid=None, name=None, **kwargs):
        """List all private images.

        :param string guid: filter based on GUID
        :param string name: filter based on name
        :param dict \\*\\*kwargs: response-level options (mask, limit, etc.)
        """
        if 'mask' not in kwargs:
            kwargs['mask'] = IMAGE_MASK

        _filter = utils.NestedDict(kwargs.get('filter') or {})
        if name:
            _filter['privateBlockDeviceTemplateGroups']['name'] = (
                utils.query_filter(name))

        if guid:
            _filter['privateBlockDeviceTemplateGroups']['globalIdentifier'] = (
                utils.query_filter(guid))

        kwargs['filter'] = _filter.to_dict()

        account = self.client['Account']
        return account.getPrivateBlockDeviceTemplateGroups(**kwargs)

    def list_public_images(self, guid=None, name=None, limit=100, **kwargs):
        """List all public images.

        :param string guid: filter based on GUID
        :param string name: filter based on name
        :param dict \\*\\*kwargs: response-level options (mask, limit, etc.)
        """
        if 'mask' not in kwargs:
            kwargs['mask'] = IMAGE_MASK

        _filter = utils.NestedDict(kwargs.get('filter') or {})
        if name:
            _filter['name'] = utils.query_filter(name)

        if guid:
            _filter['globalIdentifier'] = utils.query_filter(guid)

        kwargs['filter'] = _filter.to_dict()

        return self.vgbdtg.getPublicImages(**kwargs, limit=limit)

    def _get_ids_from_name_public(self, name):
        """Get public images which match the given name."""
        results = self.list_public_images(name=name)
        return [result['id'] for result in results]

    def _get_ids_from_name_private(self, name):
        """Get private images which match the given name."""
        results = self.list_private_images(name=name)
        return [result['id'] for result in results]

    def edit(self, image_id, name=None, note=None, tag=None):
        """Edit image related details.

        :param int image_id: The ID of the image
        :param string name: Name of the Image.
        :param string note: Note of the image.
        :param string tag: Tags of the image to be updated to.
        """
        obj = {}
        if name:
            obj['name'] = name
        if note:
            obj['note'] = note
        if obj:
            self.vgbdtg.editObject(obj, id=image_id)
        if tag:
            self.vgbdtg.setTags(str(tag), id=image_id)

        return bool(name or note or tag)

    def import_image_from_uri(self, name, uri, os_code=None, note=None,
                              ibm_api_key=None, root_key_crn=None,
                              wrapped_dek=None, cloud_init=False,
                              byol=False, is_encrypted=False):
        """Import a new image from object storage.

        :param string name: Name of the new image
        :param string uri: The URI for an object storage object
            (.vhd/.iso file) of the format:
            swift://<objectStorageAccount>@<cluster>/<container>/<objectPath>
            or (.vhd/.iso/.raw file) of the format:
            cos://<regionName>/<bucketName>/<objectPath> if using IBM Cloud
            Object Storage
        :param string os_code: The reference code of the operating system
        :param string note: Note to add to the image
        :param string ibm_api_key: Ibm Api Key needed to communicate with ICOS
            and your KMS
        :param string root_key_crn: CRN of the root key in your KMS. Go to your
            KMS (Key Protect or Hyper Protect) provider to get the CRN for your
            root key.  An example CRN:
            crn:v1:bluemix:public:hs-crypto:us-south:acctID:serviceID:key:keyID'
            Used only when is_encrypted is True.
        :param string wrapped_dek: Wrapped Data Encryption Key provided by
            your KMS. Used only when is_encrypted is True.
        :param boolean cloud_init: Specifies if image is cloud-init
        :param boolean byol: Specifies if image is bring your own license
        :param boolean is_encrypted: Specifies if image is encrypted
        """
        if 'cos://' in uri:
            return self.vgbdtg.createFromIcos({
                'name': name,
                'note': note,
                'operatingSystemReferenceCode': os_code,
                'uri': uri,
                'ibmApiKey': ibm_api_key,
                'crkCrn': root_key_crn,
                'wrappedDek': wrapped_dek,
                'cloudInit': cloud_init,
                'byol': byol,
                'isEncrypted': is_encrypted
            })
        else:
            return self.vgbdtg.createFromExternalSource({
                'name': name,
                'note': note,
                'operatingSystemReferenceCode': os_code,
                'uri': uri,
            })

    def export_image_to_uri(self, image_id, uri, ibm_api_key=None):
        """Export image into the given object storage

        :param int image_id: The ID of the image
        :param string uri: The URI for object storage of the format
            swift://<objectStorageAccount>@<cluster>/<container>/<objectPath>
            or cos://<regionName>/<bucketName>/<objectPath> if using IBM Cloud
            Object Storage
        :param string ibm_api_key: Ibm Api Key needed to communicate with IBM
            Cloud Object Storage
        """
        if 'cos://' in uri:
            return self.vgbdtg.copyToIcos({
                'uri': uri,
                'ibmApiKey': ibm_api_key
            }, id=image_id)
        else:
            return self.vgbdtg.copyToExternalSource({'uri': uri}, id=image_id)

    def add_locations(self, image_id, location_names):
        """Add available locations to an archive image template.

        :param int image_id: The ID of the image
        :param location_names: Locations for the Image.
        """
        locations = self.get_locations_list(image_id, location_names)
        return self.vgbdtg.addLocations(locations, id=image_id)

    def remove_locations(self, image_id, location_names):
        """Remove available locations from an archive image template.

        :param int image_id: The ID of the image
        :param location_names: Locations for the Image.
        """
        locations = self.get_locations_list(image_id, location_names)
        return self.vgbdtg.removeLocations(locations, id=image_id)

    def get_storage_locations(self, image_id):
        """Get available locations for public image storage.

        :param int image_id: The ID of the image
        """
        return self.vgbdtg.getStorageLocations(id=image_id)

    def get_locations_list(self, image_id, location_names):
        """Converts a list of location names to a list of locations.

        :param int image_id: The ID of the image.
        :param list location_names: A list of location names strings.
        :returns: A list of locations associated with the given location names in the image.
        """
        locations = self.get_storage_locations(image_id)
        locations_ids = []
        matching_location = {}
        output_error = "Location {} does not exist for available locations for image {}"

        for location_name in location_names:
            for location in locations:
                if location_name == location.get('name'):
                    matching_location = location
                    break
            if matching_location.get('id') is None:
                raise exceptions.SoftLayerError(output_error.format(location_name, image_id))

            locations_ids.append(matching_location)

        return locations_ids

    def share_image(self, image_id, account_id):
        """Permit sharing image template with another account.

        :param int image_id: The ID of the image.
        :param int account_id: The ID of the another account to share the image.
        """

        return self.vgbdtg.permitSharingAccess(account_id, id=image_id)

    def deny_share_image(self, image_id, account_id):
        """Deny sharing image template with another account.

        :param int image_id: The ID of the image.
        :param int account_id: The ID of the another account to deny share the image.
        """

        return self.vgbdtg.denySharingAccess(account_id, id=image_id)
