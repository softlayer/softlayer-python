"""
    SoftLayer.vs
    ~~~~~~~~~~~~
    DH Manager/helpers

    :license: MIT, see License for more details.
"""

import logging

from SoftLayer import utils

LOGGER = logging.getLogger(__name__)

class DHManager(utils.IdentifierMixin, object):
    """Manages SoftLayer Dedicated Hosts.

        See product information here https://www.ibm.com/cloud/dedicated

        Example::
            # Initialize the DHManager.
            # env variables. These can also be specified in ~/.softlayer,
            # or passed directly to SoftLayer.Client()
            # SL_USERNAME = YOUR_USERNAME
            # SL_API_KEY = YOUR_API_KEY
            import SoftLayer
            client = SoftLayer.Client()
            mgr = SoftLayer.VSManager(client)

    :param SoftLayer.API.BaseClient client: the client instance
    :param SoftLayer.managers.OrderingManager ordering_manager: an optional
                                              manager to handle ordering.
                                              If none is provided, one will be
                                              auto initialized.
    """

    #initializer
    def __init__(self, client):
        self.client = client
        self.account = client['Account']
        self.host = client['Virtual_DedicatedHost']

    def list_instances(self,tags=None, cpus=None, memory=None, name=None,
                       disk=None, datacenter=None, **kwargs):
        """Retrieve a list of all dedicated hosts on the account

        Example::

        :param list tags: filter based on list of tags
        :param integer cpus: filter based on number of CPUS
        :param integer memory: filter based on amount of memory
        :param string hostname: filter based on hostname
        :param string disk: filter based on disk
        :param string datacenter: filter based on datacenter
        :param dict \\*\\*kwargs: response-level options (mask, limit, etc.)
        :returns: Returns a list of dictionaries representing the matching
                  dedicated host.



        """
        if 'mask' not in kwargs:
            items = [
                'id',
                'name',
                'cpuCount',
                'diskCapacity',
                'memoryCapacity',
                'datacenter',
                'guestCount',
            ]
            kwargs['mask'] = "mask[%s]" % ','.join(items)

        call = 'getDedicatedHosts'

        _filter = utils.NestedDict(kwargs.get('filter') or {})
        if tags:
            _filter['dedicatedHosts']['tagReferences']['tag']['name'] = {
                'operation': 'in',
                'options': [{'name': 'data', 'value': tags}],
            }

        if name:
            _filter['dedicatedHosts']['name'] = (
                utils.query_filter(name)
            )

        if cpus:
            _filter['dedicatedHosts']['cpuCount'] = utils.query_filter(cpus)

        if disk:
            _filter['dedicatedHosts']['diskCapacity'] = (
                utils.query_filter(disk))

        if memory:
            _filter['dedicatedHosts']['memoryCapacity'] = (
                utils.query_filter(memory))

        if datacenter:
            _filter['dedicatedHosts']['datacenter']['name'] = (
                utils.query_filter(datacenter))

        kwargs['filter'] = _filter.to_dict()
        func = getattr(self.account, call)
        return func(**kwargs)