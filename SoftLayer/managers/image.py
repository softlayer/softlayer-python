"""
    SoftLayer.image
    ~~~~~~~~~~~~~~~
    Image Manager/helpers

    :license: MIT, see LICENSE for more details.
"""

from SoftLayer.utils import query_filter, NestedDict, IdentifierMixin
from SoftLayer.utils import converter

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
                      'children[blockDevices[diskImage[type]],datacenter]')
        if 'mask' not in kwargs:
            kwargs['mask'] = image_mask
        image = self.vgbdtg.getObject(id=image_id, **kwargs)
        data = self._parmateter_parsing(image)

        return image, data

    def _parmateter_parsing(self, image):
        """
        Parsing the data to get the required information
        param image: contains image related data
        """
        data = {}
        data['note'] = image.get('note')
        data['tag'] = []
        for i in range(len(image['tagReferences'])):
            data['tag'].append(image['tagReferences'][i]['tag']['name'])
        data['status'] = image['status']['name']
        data['location'] = ""
        for i in range(len(image['children'])):
            data['location'] = data['location'] + "" + \
                str((image['children'][i]['datacenter']['longName'])) + ", "
        data['location'] = data['location'][0:-2]
        totalblockdevices = image['children'][0]['blockDevices']
        blockdevices_length = len(totalblockdevices)
        capacity = [[] for i in range(blockdevices_length)]
        capacity_unit = list(capacity)
        size_on_disk = list(capacity)
        size_on_disk_unit = list(capacity)
        for i in range(blockdevices_length):
            if totalblockdevices[i]['diskImage']['type']['name'] == 'Swap':
                continue
            capacity[i] = totalblockdevices[i]['diskImage']['capacity']
            capacity_unit[i] = totalblockdevices[i]['diskImage']['units']
            size_on_disk[i] = float(totalblockdevices[i]['diskSpace'])
            size_on_disk_unit[i] = totalblockdevices[i]['units']
            size_on_disk[i], size_on_disk_unit[i] = \
                converter(size_on_disk[i], size_on_disk_unit[i])
        capacity.remove([])
        capacity_unit.remove([])
        size_on_disk.remove([])
        size_on_disk_unit.remove([])
        data['size_value'] = ""
        data['capacity_value'] = ""
        for i in range(blockdevices_length - 1):
            data['size_value'] = data['size_value'] + str(size_on_disk[i])[
                :5] + " " + str(size_on_disk_unit[i]) + "    "

            data['capacity_value'] = data['capacity_value'] + "   " + \
                str(capacity[i]) + " " + str(capacity_unit[i]) + " "
        return data

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
