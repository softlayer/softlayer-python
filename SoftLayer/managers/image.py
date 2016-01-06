"""
    SoftLayer.image
    ~~~~~~~~~~~~~~~
    Image Manager/helpers

    :license: MIT, see LICENSE for more details.
"""

from SoftLayer import utils

IMAGE_MASK = ('id,accountId,name,globalIdentifier,blockDevices,parentId,'
              'createDate,transaction')


class ImageManager(utils.IdentifierMixin, object):
    """Manages server images.

    :param SoftLayer.API.Client client: an API client instance
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

    def list_public_images(self, guid=None, name=None, **kwargs):
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

        return self.vgbdtg.getPublicImages(**kwargs)

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

    def import_image_from_uri(self, name, uri, os_code=None, note=None):
        """Import a new image from object storage.

        :param string name: Name of the new image
        :param string uri: The URI for an object storage object
            (.vhd/.iso file) of the format:
            swift://<objectStorageAccount>@<cluster>/<container>/<objectPath>
        :param string os_code: The reference code of the operating system
        :param string note: Note to add to the image
        """
        return self.vgbdtg.createFromExternalSource({
            'name': name,
            'note': note,
            'operatingSystemReferenceCode': os_code,
            'uri': uri,
        })

    def export_image_to_uri(self, image_id, uri):
        """Export image into the given object storage

        :param int image_id: The ID of the image
        :param string uri: The URI for object storage of the format
            swift://<objectStorageAccount>@<cluster>/<container>/<objectPath>
        """
        return self.vgbdtg.copyToExternalSource({'uri': uri}, id=image_id)
