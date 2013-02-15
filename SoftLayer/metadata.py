try:
    import simplejson as json
except:  # pragma: no cover
    import json # NOQA
import urllib2

from SoftLayer.consts import API_PRIVATE_ENDPOINT_REST, USER_AGENT
from SoftLayer.exceptions import SoftLayerAPIError, SoftLayerError

__all__ = ["MetadataManager"]


class MetadataManager(object):
    " MetadataManager "
    attribs = {
        'backend_mac': {'call': 'BackendMacAddresses'},
        'datacenter': {'call': 'Datacenter'},
        'datacenter_id': {'call': 'DatacenterId'},
        'domain': {'call': 'Domain'},
        'frontent_mac': {'call': 'FrontendMacAddresses'},
        'fqdn': {'call': 'FullyQualifiedDomainName'},
        'hostname': {'call': 'Hostname'},
        'id': {'call': 'Id'},
        'primary_backend_ip': {'call': 'PrimaryBackendIpAddress'},
        'primary_ip': {'call': 'PrimaryIpAddress'},
        'provision_state': {'call': 'ProvisionState'},
        'router': {'call': 'Router', 'param_req': True},
        'tags': {'call': 'Tags'},
        'user_data': {'call': 'UserMetadata'},
        'user_metadata': {'call': 'UserMetadata'},
        'vlan_ids': {'call': 'VlanIds', 'param_req': True},
        'vlans': {'call': 'Vlans', 'param_req': True},
    }

    def __init__(self, client=None):
        self.url = API_PRIVATE_ENDPOINT_REST.rstrip('/')

    def make_request(self, path):
        url = '/'.join([self.url, 'SoftLayer_Resource_Metadata', path])
        req = urllib2.Request(url)
        req.add_header('User-Agent', USER_AGENT)
        try:
            resp = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            raise SoftLayerAPIError(e.code, e.reason)
        except urllib2.URLError, e:
            raise SoftLayerAPIError(0, e.reason)
        else:
            return resp.read()

    def get(self, name, param=None):
        if name not in self.attribs:
            raise SoftLayerError('Metadata Attribute not known.')
        call_details = self.attribs[name]
        if call_details.get('param_req'):
            if not param:
                raise SoftLayerError(
                    'Parameter required to fetch this attribute')
            url = "%s/%s.json" % (self.attribs[name]['call'], param)
        else:
            url = "%s.json" % self.attribs[name]['call']
        return json.loads(self.make_request(url))
