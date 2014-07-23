"""
    SoftLayer.autoscale
    ~~~~~~~~~~~~~~~
    Autoscale Manager/helpers

    :license: MIT, see LICENSE for more details.
"""

from SoftLayer import utils

AUTOSCALE_MASK = ('regionalGroup,policies.triggers,policies.actions,'
              'loadBalancers.routingMethod,loadBalancers.routingType,'
              'loadBalancers.healthCheck.type,loadBalancers.healthCheck.attributes,loadBalancers.virtualServer')

class AutoscaleManager(utils.IdentifierMixin, object):
    """
    Manages Autoscale groups

    :param SoftLayer.API.Client client: an API client instance
    """

    def __init__(self, client):
        self.client = client
        self.client_scalegroup = self.client['Scale_Group']

    def get_group(self, group_id, **kwargs):
        """ Get details about a group

        :param int group_id: The ID of the group.
        :param dict \\*\\*kwargs: response-level options (mask, limit, etc.)
        """
        if 'mask' not in kwargs:
            kwargs['mask'] = AUTOSCALE_MASK

        x=self.client_scalegroup.getObject(id=group_id, **kwargs)
        print x
        return x

    def delete_group(self, group_id):
        """ deletes the specified group.

        :param int group_id: The ID of the group.
        """
        self.client_scalegroup.deleteObject(id=group_id)

    def list_groups(self, name=None, **kwargs):
        """ List all Autoscale groups.

        :param string name: filter based on name
        :param dict \\*\\*kwargs: response-level options (mask, limit, etc.)
        """
        if 'mask' not in kwargs:
            kwargs['mask'] = AUTOSCALE_MASK

        _filter = utils.NestedDict(kwargs.get('filter') or {})
        if name:
            _filter['name'] = (
                utils.query_filter(name))

        kwargs['filter'] = _filter.to_dict()

        account = self.client['Account']
        return account.getScaleGroups(**kwargs)

