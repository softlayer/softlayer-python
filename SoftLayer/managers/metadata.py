"""
    SoftLayer.metadata
    ~~~~~~~~~~~~~~~~~~
    Metadata Manager/helpers

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer.API import BaseClient
from SoftLayer import consts
from SoftLayer import exceptions
from SoftLayer import transports


METADATA_MAPPING = {
    'backend_mac': {'call': 'getBackendMacAddresses'},
    'datacenter': {'call': 'getDatacenter'},
    'datacenter_id': {'call': 'getDatacenterId'},
    'domain': {'call': 'getDomain'},
    'frontend_mac': {'call': 'getFrontendMacAddresses'},
    'fqdn': {'call': 'getFullyQualifiedDomainName'},
    'hostname': {'call': 'getHostname'},
    'id': {'call': 'getId'},
    'primary_backend_ip': {'call': 'getPrimaryBackendIpAddress'},
    'primary_ip': {'call': 'getPrimaryIpAddress'},
    'primary_frontend_ip': {'call': 'getPrimaryIpAddress'},
    'provision_state': {'call': 'getProvisionState'},
    'router': {'call': 'getRouter', 'param_req': True},
    'tags': {'call': 'getTags'},
    'user_data': {'call': 'getUserMetadata'},
    'user_metadata': {'call': 'getUserMetadata'},
    'vlan_ids': {'call': 'getVlanIds', 'param_req': True},
    'vlans': {'call': 'getVlans', 'param_req': True},
}
METADATA_ATTRIBUTES = METADATA_MAPPING.keys()


class MetadataManager(object):
    """Provides an interface for the SoftLayer metadata service.

    See product information here:
    http://sldn.softlayer.com/reference/services/SoftLayer_Resource_Metadata

    This provides metadata about the resourse it is called from.
    See `METADATA_ATTRIBUTES` for full list of attributes.

        Usage:

            >>> import SoftLayer
            >>> client = SoftLayer.create_client_from_env()
            >>> from SoftLayer import MetadataManager
            >>> meta = MetadataManager(client)
            >>> meta.get('datacenter')
            'dal05'
            >>> meta.get('fqdn')
            'test.example.com'

    :param SoftLayer.API.BaseClient client: the client instance

    """

    attribs = METADATA_MAPPING

    def __init__(self, client=None, timeout=5):
        if client is None:
            transport = transports.RestTransport(
                timeout=timeout,
                endpoint_url=consts.API_PRIVATE_ENDPOINT_REST,
            )
            client = BaseClient(transport=transport)

        self.client = client

    def get(self, name, param=None):
        """Retreive a metadata attribute.

        :param string name: name of the attribute to retrieve. See `attribs`
        :param param: Required parameter for some attributes

        """
        if name not in self.attribs:
            raise exceptions.SoftLayerError('Unknown metadata attribute.')

        call_details = self.attribs[name]

        if call_details.get('param_req'):
            if not param:
                raise exceptions.SoftLayerError(
                    'Parameter required to get this attribute.')

        params = tuple()
        if param is not None:
            params = (param,)
        try:
            return self.client.call('Resource_Metadata',
                                    self.attribs[name]['call'],
                                    *params)
        except exceptions.SoftLayerAPIError as ex:
            if ex.faultCode == 404:
                return None
            raise ex

    def _get_network(self, kind, router=True, vlans=True, vlan_ids=True):
        """Wrapper for getting details about networks.

            :param string kind: network kind. Typically 'public' or 'private'
            :param boolean router: flag to include router information
            :param boolean vlans: flag to include vlan information
            :param boolean vlan_ids: flag to include vlan_ids

        """
        network = {}
        macs = self.get('%s_mac' % kind)
        network['mac_addresses'] = macs

        if len(macs) == 0:
            return network

        if router:
            network['router'] = self.get('router', macs[0])

        if vlans:
            network['vlans'] = self.get('vlans', macs[0])

        if vlan_ids:
            network['vlan_ids'] = self.get('vlan_ids', macs[0])

        return network

    def public_network(self, **kwargs):
        """Returns details about the public network.

        :param boolean router: True to return router details
        :param boolean vlans: True to return vlan details
        :param boolean vlan_ids: True to return vlan_ids

        """
        return self._get_network('frontend', **kwargs)

    def private_network(self, **kwargs):
        """Returns details about the private network.

        :param boolean router: True to return router details
        :param boolean vlans: True to return vlan details
        :param boolean vlan_ids: True to return vlan_ids

        """
        return self._get_network('backend', **kwargs)
