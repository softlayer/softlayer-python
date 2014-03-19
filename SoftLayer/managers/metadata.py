"""
    SoftLayer.metadata
    ~~~~~~~~~~~~~~~~~~
    Metadata Manager/helpers

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer.transports import make_rest_api_call
from SoftLayer.consts import API_PRIVATE_ENDPOINT_REST, USER_AGENT
from SoftLayer.exceptions import SoftLayerAPIError, SoftLayerError


METADATA_MAPPING = {
    'backend_mac': {'call': 'BackendMacAddresses'},
    'datacenter': {'call': 'Datacenter'},
    'datacenter_id': {'call': 'DatacenterId'},
    'domain': {'call': 'Domain'},
    'frontend_mac': {'call': 'FrontendMacAddresses'},
    'fqdn': {'call': 'FullyQualifiedDomainName'},
    'hostname': {'call': 'Hostname'},
    'id': {'call': 'Id'},
    'primary_backend_ip': {'call': 'PrimaryBackendIpAddress'},
    'primary_ip': {'call': 'PrimaryIpAddress'},
    'primary_frontend_ip': {'call': 'PrimaryIpAddress'},
    'provision_state': {'call': 'ProvisionState'},
    'router': {'call': 'Router', 'param_req': True},
    'tags': {'call': 'Tags'},
    'user_data': {'call': 'UserMetadata'},
    'user_metadata': {'call': 'UserMetadata'},
    'vlan_ids': {'call': 'VlanIds', 'param_req': True},
    'vlans': {'call': 'Vlans', 'param_req': True},
}
METADATA_ATTRIBUTES = METADATA_MAPPING.keys()


class MetadataManager(object):
    """ Provides an interface for the metadata service. This provides metadata
        about the resourse it is called from. See `METADATA_ATTRIBUTES` for
        full list of attributes.

        Usage:

            >>> import SoftLayer
            >>> client = SoftLayer.Client()
            >>> from SoftLayer import MetadataManager
            >>> meta = MetadataManager(client)
            >>> meta.get('datacenter')
            'dal05'
            >>> meta.get('fqdn')
            'test.example.com'

    """

    attribs = METADATA_MAPPING

    def __init__(self, client=None, timeout=5):
        self.url = API_PRIVATE_ENDPOINT_REST.rstrip('/')
        self.timeout = timeout
        self.client = client

    def make_request(self, path):
        """ Make a request against the metadata service

        :param string path: path to the specific metadata resource
        """
        url = '/'.join([self.url, 'SoftLayer_Resource_Metadata', path])
        try:
            return make_rest_api_call('GET', url,
                                      http_headers={'User-Agent': USER_AGENT},
                                      timeout=self.timeout)
        except SoftLayerAPIError as ex:
            if ex.faultCode == 404:
                return None
            raise ex

    def get(self, name, param=None):
        """ Retreive a metadata attribute

        :param string name: name of the attribute to retrieve. See `attribs`
        :param param: Required parameter for some attributes

        """
        if name not in self.attribs:
            raise SoftLayerError('Unknown metadata attribute.')

        call_details = self.attribs[name]
        extension = '.json'
        if self.attribs[name]['call'] == 'UserMetadata':
            extension = '.txt'

        if call_details.get('param_req'):
            if not param:
                raise SoftLayerError(
                    'Parameter required to get this attribute.')
            path = "%s/%s%s" % (self.attribs[name]['call'], param, extension)
        else:
            path = "%s%s" % (self.attribs[name]['call'], extension)

        return self.make_request(path)

    def _get_network(self, kind, router=True, vlans=True, vlan_ids=True):
        """ Wrapper for getting details about networks

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
        """ Returns details about the public network

        :param boolean router: True to return router details
        :param boolean vlans: True to return vlan details
        :param boolean vlan_ids: True to return vlan_ids

        """
        return self._get_network('frontend', **kwargs)

    def private_network(self, **kwargs):
        """ Returns details about the private network

        :param boolean router: True to return router details
        :param boolean vlans: True to return vlan details
        :param boolean vlan_ids: True to return vlan_ids

        """
        return self._get_network('backend', **kwargs)
