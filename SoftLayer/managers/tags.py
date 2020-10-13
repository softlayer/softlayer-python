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
        service = self.type_to_service(tag_type)
        if service is None:
            raise SoftLayerAPIError(404, "Unable to lookup {} types".format(tag_type))
        return self.client.call(service, 'getObject', id=resource_table_id)

    def delete_tag(self, name):
        """Calls SoftLayer_Tag::deleteTag

        :param string name: tag name to delete
        """
        return self.client.call('SoftLayer_Tag', 'deleteTag', name)

    def set_tags(self, tags, key_name, resource_id):
        """Calls SoftLayer_Tag::setTags()

        :param string tags: List of tags.
        :param string key_name: Key name of a tag type.
        :param int resource_id: ID of the object being tagged.
        """
        return self.client.call('SoftLayer_Tag', 'setTags', tags, key_name, resource_id)

    def get_all_tag_types(self):
        """Calls SoftLayer_Tag::getAllTagTypes()"""
        types = self.client.call('SoftLayer_Tag', 'getAllTagTypes')
        useable_types = []
        for tag_type in types:
            service = self.type_to_service(tag_type['keyName'])
            # Mostly just to remove the types that are not user taggable.
            if service is not None:
                temp_type = tag_type
                temp_type['service'] = service
                useable_types.append(temp_type)
        return useable_types

    def taggable_by_type(self, tag_type):
        """Returns a list of resources that can be tagged, that are of the given type

        :param string tag_type: Key name of a tag type. See SoftLayer_Tag::getAllTagTypes
        """
        service = self.type_to_service(tag_type)
        search_term = "_objectType:SoftLayer_{}".format(service)
        if tag_type == 'TICKET':
            search_term = "{} status.name: open".format(search_term)
        elif tag_type == 'IMAGE_TEMPLATE':
            mask = "mask[id,accountId,name,globalIdentifier,parentId,publicFlag,flexImageFlag,imageType]"
            resources = self.client.call('SoftLayer_Account', 'getPrivateBlockDeviceTemplateGroups',
                                         mask=mask, iter=True)
            to_return = []
            # Fake search result output
            for resource in resources:
                to_return.append({'resourceType': service, 'resource': resource})
            return to_return
        elif tag_type == 'NETWORK_SUBNET':
            resources = self.client.call('SoftLayer_Account', 'getSubnets', iter=True)
            to_return = []
            # Fake search result output
            for resource in resources:
                to_return.append({'resourceType': service, 'resource': resource})
            return to_return
        resources = self.client.call('SoftLayer_Search', 'advancedSearch', search_term, iter=True)
        return resources

    @staticmethod
    def type_to_service(tag_type):
        """Returns the SoftLayer service for the given tag_type"""
        service = None
        if tag_type in ['ACCOUNT_DOCUMENT', 'CONTRACT']:
            return None

        if tag_type == 'APPLICATION_DELIVERY_CONTROLLER':
            service = 'Network_Application_Delivery_Controller'
        elif tag_type == 'GUEST':
            service = 'Virtual_Guest'
        elif tag_type == 'DEDICATED_HOST':
            service = 'Virtual_DedicatedHost'
        elif tag_type == 'IMAGE_TEMPLATE':
            service = 'Virtual_Guest_Block_Device_Template_Group'
        else:

            tag_type = tag_type.lower()
            # Sets the First letter, and any letter preceeded by a '_' to uppercase
            # HARDWARE -> Hardware, NETWORK_VLAN -> Network_Vlan for example.
            service = re.sub(r'(^[a-z]|\_[a-z])', lambda x: x.group().upper(), tag_type)
        return service

    @staticmethod
    def get_resource_name(resource, tag_type):
        """Returns a string that names a resource

        :param dict resource: A SoftLayer datatype for the given tag_type
        :param string tag_type: Key name for the tag_type
        """
        if tag_type == 'NETWORK_VLAN_FIREWALL':
            return resource.get('primaryIpAddress')
        elif tag_type == 'NETWORK_VLAN':
            return "{} ({})".format(resource.get('vlanNumber'), resource.get('name'))
        elif tag_type == 'IMAGE_TEMPLATE' or tag_type == 'APPLICATION_DELIVERY_CONTROLLER':
            return resource.get('name')
        elif tag_type == 'TICKET':
            return resource.get('subjet')
        elif tag_type == 'NETWORK_SUBNET':
            return resource.get('networkIdentifier')
        else:
            return resource.get('fullyQualifiedDomainName')

    # @staticmethod
    # def type_to_datatype(tag_type):
    #     """Returns the SoftLayer datatye for the given tag_type"""
    #     datatye = None
    #     if tag_type in ['ACCOUNT_DOCUMENT', 'CONTRACT']:
    #         return None

    #     if tag_type == 'APPLICATION_DELIVERY_CONTROLLER':
    #         datatye = 'adcLoadBalancers'
    #     elif tag_type == 'GUEST':
    #         datatye = 'virtualGuests'
    #     elif tag_type == 'DEDICATED_HOST':
    #         datatye = 'dedicatedHosts'
    #     elif tag_type == 'HARDWARE':
    #         datatye = 'hardware'
    #     elif tag_type == 'TICKET':
    #         datatye = 'openTickets'
    #     elif tag_type == 'NETWORK_SUBNET':
    #         datatye = 'subnets'
    #     elif tag_type == 'NETWORK_VLAN':
    #         datatye = 'networkVlans'
    #     elif tag_type == 'NETWORK_VLAN_FIREWALL':
    #         datatye = 'networkVlans'
    #     elif tag_type == 'IMAGE_TEMPLATE':
    #         datatye = 'blockDeviceTemplateGroups'

    #     return datatye
