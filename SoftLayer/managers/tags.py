"""
    SoftLayer.tags
    ~~~~~~~~~~~~
    Tag Manager

    :license: MIT, see LICENSE for more details.
"""
import re

from SoftLayer.exceptions import SoftLayerAPIError


class TagManager(object):
    """Manager for Tag functions."""

    def __init__(self, client):
        self.client = client

    def list_tags(self, mask=None):
        """Returns a list of all tags for the Current User

        :param str mask: Object mask to use if you do not want the default.
        """
        if mask is None:
            mask = "mask[id,name,referenceCount]"
        unattached = self.get_unattached_tags(mask)
        attached = self.get_attached_tags(mask)
        return {'attached': attached, 'unattached': unattached}

    def get_unattached_tags(self, mask=None):
        """Calls SoftLayer_Tag::getUnattachedTagsForCurrentUser()

        :params string mask: Mask to use.
        """
        return self.client.call('SoftLayer_Tag', 'getUnattachedTagsForCurrentUser',
                                mask=mask, iter=True)

    def get_attached_tags(self, mask=None):
        """Calls SoftLayer_Tag::getAttachedTagsForCurrentUser()

        :params string mask: Mask to use.
        """
        return self.client.call('SoftLayer_Tag', 'getAttachedTagsForCurrentUser',
                                mask=mask, iter=True)

    def get_tag_references(self, tag_id, mask=None):
        """Calls SoftLayer_Tag::getReferences(id=tag_id)

        :params int tag_id: Tag id to get references from
        :params string mask: Mask to use.
        """
        if mask is None:
            mask = "mask[tagType]"
        return self.client.call('SoftLayer_Tag', 'getReferences', id=tag_id, mask=mask, iter=True)

    def get_tag(self, tag_id, mask=None):
        """Calls SoftLayer_Tag::getObject(id=tag_id)

        :params int tag_id: Tag id to get object from
        :params string mask: Mask to use.
        """
        if mask is None:
            mask = "mask[id,name]"
        result = self.client.call('SoftLayer_Tag', 'getObject', id=tag_id, mask=mask)
        return result

    def get_tag_by_name(self, tag_name, mask=None):
        """Calls SoftLayer_Tag::getTagByTagName(tag_name)

        :params string tag_name: Tag name to get object from
        :params string mask: Mask to use.
        """
        if mask is None:
            mask = "mask[id,name]"
        result = self.client.call('SoftLayer_Tag', 'getTagByTagName', tag_name, mask=mask)
        return result

    def reference_lookup(self, resource_table_id, tag_type):
        """Returns the SoftLayer Service for the corresponding type

        :param int resource_table_id: Tag_Reference::resourceTableId
        :param string tag_type: Tag_Reference->tagType->keyName

        From  SoftLayer_Tag::getAllTagTypes()

        |Type                             |Service |
        | -----------------------------   | ------ |
        |Hardware                         |HARDWARE|
        |CCI                              |GUEST|
        |Account Document                 |ACCOUNT_DOCUMENT|
        |Ticket                           |TICKET|
        |Vlan Firewall                    |NETWORK_VLAN_FIREWALL|
        |Contract                         |CONTRACT|
        |Image Template                   |IMAGE_TEMPLATE|
        |Application Delivery Controller  |APPLICATION_DELIVERY_CONTROLLER|
        |Vlan                             |NETWORK_VLAN|
        |Dedicated Host                   |DEDICATED_HOST|
        """

        if tag_type in ['ACCOUNT_DOCUMENT', 'CONTRACT']:
            raise SoftLayerAPIError(404, "Unable to lookup {} types".format(tag_type))

        if tag_type == 'APPLICATION_DELIVERY_CONTROLLER':
            service = 'Network_Application_Delivery_Controller'
        elif tag_type == 'GUEST':
            service = 'Virtual_Guest'
        elif tag_type == 'DEDICATED_HOST':
            service = 'Virtual_DedicatedHost'
        else:

            tag_type = tag_type.lower()
            # Sets the First letter, and any letter preceeded by a '_' to uppercase
            # HARDWARE -> Hardware, NETWORK_VLAN -> Network_Vlan for example.
            service = re.sub(r'(^[a-z]|\_[a-z])', lambda x: x.group().upper(), tag_type)

        # return {}
        return self.client.call(service, 'getObject', id=resource_table_id)

    def set_tags(self, tags, key_name, resource_id):
        """Calls SoftLayer_Tag::setTags()

        :param string tags: List of tags.
        :param string key_name: Key name of a tag type.
        :param int resource_id: ID of the object being tagged.
        """
        return self.client.call('SoftLayer_Tag', 'setTags', tags, key_name, resource_id)
