"""
    SoftLayer.image
    ~~~~~~~~~~~~~~~
    Image Manager/helpers

    :license: MIT, see LICENSE for more details.
"""

from SoftLayer.utils import query_filter, NestedDict, IdentifierMixin

IMAGE_MASK = ('id,accountId,name,globalIdentifier,blockDevices,parentId,'
              'createDate')


class ImageManager(IdentifierMixin, object):
    """
    Manages server images

    :param SoftLayer.API.Client client: an API client instance
    """

    def __init__(self, client):
        self.client = client
        self.vgbdtg = self.client['Virtual_Guest_Block_Device_Template_Group']
        self.resolvers = [self._get_ids_from_name_public,
                          self._get_ids_from_name_private]

    def get_image(self, image_id, **kwargs):
        """ Get details about an image

        :param int image: The ID of the image.
        :param dict \\*\\*kwargs: response-level options (mask, limit, etc.)
        """
        image_mask = ('id,accountId,name,globalIdentifier,blockDevices,'
                      'parentId,createDate,note,status,tagReferences[tag],'
                      'children[blockDevices[diskImage[type]]]')
        if 'mask' not in kwargs:
            kwargs['mask'] = image_mask

        return self.vgbdtg.getObject(id=image_id, **kwargs)

    def delete_image(self, image_id):
        """ deletes the specified image.

        :param int image: The ID of the image.
        """
        self.vgbdtg.deleteObject(id=image_id)

    def list_private_images(self, guid=None, name=None, **kwargs):
        """ List all private images.

        :param string guid: filter based on GUID
        :param string name: filter based on name
        :param dict \\*\\*kwargs: response-level options (mask, limit, etc.)
        """
        if 'mask' not in kwargs:
            kwargs['mask'] = IMAGE_MASK

        _filter = NestedDict(kwargs.get('filter') or {})
        if name:
            _filter['privateBlockDeviceTemplateGroups']['name'] = \
                query_filter(name)

        if guid:
            _filter['privateBlockDeviceTemplateGroups']['globalIdentifier'] = \
                query_filter(guid)

        kwargs['filter'] = _filter.to_dict()

        account = self.client['Account']
        return account.getPrivateBlockDeviceTemplateGroups(**kwargs)

    def list_public_images(self, guid=None, name=None, **kwargs):
        """ List all public images.

        :param string guid: filter based on GUID
        :param string name: filter based on name
        :param dict \\*\\*kwargs: response-level options (mask, limit, etc.)
        """
        if 'mask' not in kwargs:
            kwargs['mask'] = IMAGE_MASK

        _filter = NestedDict(kwargs.get('filter') or {})
        if name:
            _filter['name'] = query_filter(name)

        if guid:
            _filter['globalIdentifier'] = query_filter(guid)

        kwargs['filter'] = _filter.to_dict()

        return self.vgbdtg.getPublicImages(**kwargs)

    def _get_ids_from_name_public(self, name):
        """ Get public images which match the given name """
        results = self.list_public_images(name=name)
        return [result['id'] for result in results]

    def _get_ids_from_name_private(self, name):
        """ Get private images which match the given name """
        results = self.list_private_images(name=name)
        return [result['id'] for result in results]
