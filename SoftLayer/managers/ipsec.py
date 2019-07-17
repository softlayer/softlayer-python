"""
    SoftLayer.ipsec
    ~~~~~~~~~~~~~~~~~~
    IPSec VPN Manager

    :license: MIT, see LICENSE for more details.
"""

from SoftLayer.exceptions import SoftLayerAPIError
from SoftLayer import utils


class IPSECManager(utils.IdentifierMixin, object):
    """Manage SoftLayer IPSEC VPN tunnel contexts.

    This provides helpers to manage IPSEC contexts, private and remote subnets,
    and NAT translations.

    :param SoftLayer.API.BaseClient client: the client instance
    :param SoftLayer.API.BaseClient account: account service client
    :param SoftLayer.API.BaseClient context: tunnel context client
    :param SoftLayer.API.BaseClient customer_subnet: remote subnet client
    """

    def __init__(self, client):
        self.client = client
        self.account = client['Account']
        self.context = client['Network_Tunnel_Module_Context']
        self.remote_subnet = client['Network_Customer_Subnet']

    def add_internal_subnet(self, context_id, subnet_id):
        """Add an internal subnet to a tunnel context.

        :param int context_id: The id-value representing the context instance.
        :param int subnet_id: The id-value representing the internal subnet.
        :return bool: True if internal subnet addition was successful.
        """
        return self.context.addPrivateSubnetToNetworkTunnel(subnet_id,
                                                            id=context_id)

    def add_remote_subnet(self, context_id, subnet_id):
        """Adds a remote subnet to a tunnel context.

        :param int context_id: The id-value representing the context instance.
        :param int subnet_id: The id-value representing the remote subnet.
        :return bool: True if remote subnet addition was successful.
        """
        return self.context.addCustomerSubnetToNetworkTunnel(subnet_id,
                                                             id=context_id)

    def add_service_subnet(self, context_id, subnet_id):
        """Adds a service subnet to a tunnel context.

        :param int context_id: The id-value representing the context instance.
        :param int subnet_id: The id-value representing the service subnet.
        :return bool: True if service subnet addition was successful.
        """
        return self.context.addServiceSubnetToNetworkTunnel(subnet_id,
                                                            id=context_id)

    def apply_configuration(self, context_id):
        """Requests network configuration for a tunnel context.

        :param int context_id: The id-value representing the context instance.
        :return bool: True if the configuration request was successfully queued.
        """
        return self.context.applyConfigurationsToDevice(id=context_id)

    def create_remote_subnet(self, account_id, identifier, cidr):
        """Creates a remote subnet on the given account.

        :param string account_id: The account identifier.
        :param string identifier: The network identifier of the remote subnet.
        :param string cidr: The CIDR value of the remote subnet.
        :return dict: Mapping of properties for the new remote subnet.
        """
        return self.remote_subnet.createObject({
            'accountId': account_id,
            'cidr': cidr,
            'networkIdentifier': identifier
        })

    def create_translation(self, context_id, static_ip, remote_ip, notes):
        """Creates an address translation on a tunnel context/

        :param int context_id: The id-value representing the context instance.
        :param string static_ip: The IP address value representing the
               internal side of the translation entry,
        :param string remote_ip: The IP address value representing the remote
               side of the translation entry,
        :param string notes: The notes to supply with the translation entry,
        :return dict: Mapping of properties for the new translation entry.
        """
        return self.context.createAddressTranslation({
            'customerIpAddress': remote_ip,
            'internalIpAddress': static_ip,
            'notes': notes
        }, id=context_id)

    def delete_remote_subnet(self, subnet_id):
        """Deletes a remote subnet from the current account.

        :param string subnet_id: The id-value representing the remote subnet.
        :return bool: True if subnet deletion was successful.
        """
        return self.remote_subnet.deleteObject(id=subnet_id)

    def get_tunnel_context(self, context_id, **kwargs):
        """Retrieves the network tunnel context instance.

        :param int context_id: The id-value representing the context instance.
        :return dict: Mapping of properties for the tunnel context.
        :raise SoftLayerAPIError: If a context cannot be found.
        """
        _filter = utils.NestedDict(kwargs.get('filter') or {})
        _filter['networkTunnelContexts']['id'] = utils.query_filter(context_id)

        kwargs['filter'] = _filter.to_dict()
        contexts = self.account.getNetworkTunnelContexts(**kwargs)
        if len(contexts) == 0:
            raise SoftLayerAPIError('SoftLayer_Exception_ObjectNotFound',
                                    'Unable to find object with id of \'{}\''
                                    .format(context_id))
        return contexts[0]

    def get_translation(self, context_id, translation_id):
        """Retrieves a translation entry for the given id values.

        :param int context_id: The id-value representing the context instance.
        :param int translation_id: The id-value representing the translation
               instance.
        :return dict: Mapping of properties for the translation entry.
        :raise SoftLayerAPIError: If a translation cannot be found.
        """
        translation = next((x for x in self.get_translations(context_id)
                            if x['id'] == translation_id), None)
        if translation is None:
            raise SoftLayerAPIError('SoftLayer_Exception_ObjectNotFound',
                                    'Unable to find object with id of \'{}\''
                                    .format(translation_id))
        return translation

    def get_translations(self, context_id):
        """Retrieves all translation entries for a tunnel context.

        :param int context_id: The id-value representing the context instance.
        :return list(dict): Translations associated with the given context
        """
        _mask = ('[mask[addressTranslations[customerIpAddressRecord,'
                 'internalIpAddressRecord]]]')
        context = self.get_tunnel_context(context_id, mask=_mask)
        # Pull the internal and remote IP addresses into the translation
        for translation in context.get('addressTranslations', []):
            remote_ip = translation.get('customerIpAddressRecord', {})
            internal_ip = translation.get('internalIpAddressRecord', {})
            translation['customerIpAddress'] = remote_ip.get('ipAddress', '')
            translation['internalIpAddress'] = internal_ip.get('ipAddress', '')
            translation.pop('customerIpAddressRecord', None)
            translation.pop('internalIpAddressRecord', None)
        return context['addressTranslations']

    def get_tunnel_contexts(self, **kwargs):
        """Retrieves network tunnel module context instances.

        :return list(dict): Contexts associated with the current account.
        """
        return self.account.getNetworkTunnelContexts(**kwargs)

    def remove_internal_subnet(self, context_id, subnet_id):
        """Remove an internal subnet from a tunnel context.

        :param int context_id: The id-value representing the context instance.
        :param int subnet_id: The id-value representing the internal subnet.
        :return bool: True if internal subnet removal was successful.
        """
        return self.context.removePrivateSubnetFromNetworkTunnel(subnet_id,
                                                                 id=context_id)

    def remove_remote_subnet(self, context_id, subnet_id):
        """Removes a remote subnet from a tunnel context.

        :param int context_id: The id-value representing the context instance.
        :param int subnet_id: The id-value representing the remote subnet.
        :return bool: True if remote subnet removal was successful.
        """
        return self.context.removeCustomerSubnetFromNetworkTunnel(subnet_id,
                                                                  id=context_id)

    def remove_service_subnet(self, context_id, subnet_id):
        """Removes a service subnet from a tunnel context.

        :param int context_id: The id-value representing the context instance.
        :param int subnet_id: The id-value representing the service subnet.
        :return bool: True if service subnet removal was successful.
        """
        return self.context.removeServiceSubnetFromNetworkTunnel(subnet_id,
                                                                 id=context_id)

    def remove_translation(self, context_id, translation_id):
        """Removes a translation entry from a tunnel context.

        :param int context_id: The id-value representing the context instance.
        :param int translation_id: The id-value representing the translation.
        :return bool: True if translation entry removal was successful.
        """
        return self.context.deleteAddressTranslation(translation_id,
                                                     id=context_id)

    def update_translation(self, context_id, translation_id, static_ip=None,
                           remote_ip=None, notes=None):
        """Updates an address translation entry using the given values.

        :param int context_id: The id-value representing the context instance.
        :param dict template: A key-value mapping of translation properties.
        :param string static_ip: The static IP address value to update.
        :param string remote_ip: The remote IP address value to update.
        :param string notes: The notes value to update.
        :return bool: True if the update was successful.
        """
        translation = self.get_translation(context_id, translation_id)

        if static_ip is not None:
            translation['internalIpAddress'] = static_ip
            translation.pop('internalIpAddressId', None)
        if remote_ip is not None:
            translation['customerIpAddress'] = remote_ip
            translation.pop('customerIpAddressId', None)
        if notes is not None:
            translation['notes'] = notes
        self.context.editAddressTranslation(translation, id=context_id)
        return True

    def update_tunnel_context(self, context_id, friendly_name=None,
                              remote_peer=None, preshared_key=None,
                              phase1_auth=None, phase1_crypto=None,
                              phase1_dh=None, phase1_key_ttl=None,
                              phase2_auth=None, phase2_crypto=None,
                              phase2_dh=None, phase2_forward_secrecy=None,
                              phase2_key_ttl=None):
        """Updates a tunnel context using the given values.

        :param string context_id: The id-value representing the context.
        :param string friendly_name: The friendly name value to update.
        :param string remote_peer: The remote peer IP address value to update.
        :param string preshared_key: The preshared key value to update.
        :param string phase1_auth: The phase 1 authentication value to update.
        :param string phase1_crypto: The phase 1 encryption value to update.
        :param string phase1_dh: The phase 1 diffie hellman group value
               to update.
        :param string phase1_key_ttl: The phase 1 key life value to update.
        :param string phase2_auth: The phase 2 authentication value to update.
        :param string phase2_crypto: The phase 2 encryption value to update.
        :param string phase2_df: The phase 2 diffie hellman group value
               to update.
        :param string phase2_forward_secriecy: The phase 2 perfect forward
               secrecy value to update.
        :param string phase2_key_ttl: The phase 2 key life value to update.
        :return bool: True if the update was successful.
        """
        context = self.get_tunnel_context(context_id)

        if friendly_name is not None:
            context['friendlyName'] = friendly_name
        if remote_peer is not None:
            context['customerPeerIpAddress'] = remote_peer
        if preshared_key is not None:
            context['presharedKey'] = preshared_key
        if phase1_auth is not None:
            context['phaseOneAuthentication'] = phase1_auth
        if phase1_crypto is not None:
            context['phaseOneEncryption'] = phase1_crypto
        if phase1_dh is not None:
            context['phaseOneDiffieHellmanGroup'] = phase1_dh
        if phase1_key_ttl is not None:
            context['phaseOneKeylife'] = phase1_key_ttl
        if phase2_auth is not None:
            context['phaseTwoAuthentication'] = phase2_auth
        if phase2_crypto is not None:
            context['phaseTwoEncryption'] = phase2_crypto
        if phase2_dh is not None:
            context['phaseTwoDiffieHellmanGroup'] = phase2_dh
        if phase2_forward_secrecy is not None:
            context['phaseTwoPerfectForwardSecrecy'] = phase2_forward_secrecy
        if phase2_key_ttl is not None:
            context['phaseTwoKeylife'] = phase2_key_ttl
        return self.context.editObject(context, id=context_id)
