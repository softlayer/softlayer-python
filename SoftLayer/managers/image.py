"""
    SoftLayer.image
    ~~~~~~~~~~~~~~~
    Hardware Manager/helpers

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
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
        #: A valid `SoftLayer.API.Client` object that will be used for all
        #: actions.
        self.client = client
        #: Reference to the Virtual_Guest_Block_Device_Template_Group API
        #: object.
        self.vgbdtg = self.client['Virtual_Guest_Block_Device_Template_Group']
        #: A list of resolver functions. Used primarily by the CLI to provide
        #: a variety of methods for uniquely identifying an object such as guid
        self.resolvers = [self._get_ids_from_guid_public,
                          self._get_ids_from_guid_private,
                          self._get_ids_from_name_public,
                          self._get_ids_from_name_private]

    def get_image(self, image_id, **kwargs):
        """ Get details about an image

        :param int image: The ID of the image.
        :param dict \*\*kwargs: response-level arguments (limit, offset, etc.)
        """
        if 'mask' not in kwargs:
            kwargs['mask'] = IMAGE_MASK

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
        :param dict \*\*kwargs: response-level arguments (limit, offset, etc.)
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
        :param dict \*\*kwargs: response-level arguments (limit, offset, etc.)
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
        results = self.list_public_images(name=name)
        return [result['id'] for result in results]

    def _get_ids_from_name_private(self, name):
        results = self.list_private_images(name=name)
        return [result['id'] for result in results]

    def _get_ids_from_guid_public(self, guid):
        if len(guid) != 36:
            return
        results = self.list_public_images(guid=guid)
        return [result['id'] for result in results]

    def _get_ids_from_guid_private(self, guid):
        if len(guid) != 36:
            return
        results = self.list_private_images(guid=guid)
        return [result['id'] for result in results]
