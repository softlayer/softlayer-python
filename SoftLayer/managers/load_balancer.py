"""
    SoftLayer.load_balancer
    ~~~~~~~~~~~~~~~~~~~~~~~
    Load Balancer Manager/helpers

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import exceptions
from SoftLayer.managers import ordering
from SoftLayer import utils


class LoadBalancerManager(utils.IdentifierMixin, object):
    """Manages SoftLayer load balancers.

    See product information here: https://www.ibm.com/cloud/load-balancer

    :param SoftLayer.API.BaseClient client: the client instance

    """

    def __init__(self, client):
        self.client = client
        self.account = self.client['Account']
        self.prod_pkg = self.client['Product_Package']
        # Citrix Netscalers
        self.adc = self.client['Network_Application_Delivery_Controller']
        # IBM CLoud LB
        self.lbaas = self.client['Network_LBaaS_LoadBalancer']
        self.package_keyname = 'LBAAS'

    def get_adcs(self, mask=None):
        """Returns a list of all netscalers.

        :returns: SoftLayer_Network_Application_Delivery_Controller[].
        """
        if mask is None:
            mask = 'mask[managementIpAddress,outboundPublicBandwidthUsage,primaryIpAddress,datacenter]'
        return self.account.getApplicationDeliveryControllers(mask=mask)

    def get_adc(self, identifier, mask=None):
        """Returns a netscaler object.

        :returns: SoftLayer_Network_Application_Delivery_Controller.
        """
        if mask is None:
            mask = "mask[networkVlans, password, managementIpAddress, primaryIpAddress, subnets, tagReferences, " \
                   "licenseExpirationDate, datacenter]"
        return self.adc.getObject(id=identifier, mask=mask)

    def get_lbaas(self, mask=None):
        """Returns a list of IBM Cloud Loadbalancers

        :returns: SoftLayer_Network_LBaaS_LoadBalancer[]
        """
        if mask is None:
            mask = "mask[datacenter,listenerCount,memberCount]"
        this_lb = self.lbaas.getAllObjects(mask=mask)

        return this_lb

    def get_lb(self, identifier, mask=None):
        """Returns a IBM Cloud LoadBalancer

        :returns: SoftLayer_Network_LBaaS_LoadBalancer
        """
        if mask is None:
            mask = "mask[healthMonitors, l7Pools,  members, sslCiphers, " \
                   "listeners[defaultPool[healthMonitor, members, sessionAffinity],l7Policies]]"

        this_lb = self.lbaas.getObject(id=identifier, mask=mask)
        health = self.lbaas.getLoadBalancerMemberHealth(this_lb.get('uuid'))

        this_lb['health'] = health
        return this_lb

    def update_lb_health_monitors(self, uuid, checks):
        """calls SoftLayer_Network_LBaaS_HealthMonitor::updateLoadBalancerHealthMonitors()

        - `updateLoadBalancerHealthMonitors <https://sldn.softlayer.com/reference/services/SoftLayer_Network_LBaaS_\
            HealthMonitor/updateLoadBalancerHealthMonitors/>`_
        - `SoftLayer_Network_LBaaS_LoadBalancerHealthMonitorConfiguration <https://sldn.softlayer.com/reference/\
            datatypes/SoftLayer_Network_LBaaS_LoadBalancerHealthMonitorConfiguration/>`_

        :param uuid: loadBalancerUuid
        :param checks list: SoftLayer_Network_LBaaS_LoadBalancerHealthMonitorConfiguration[]
        """

        # return self.lbaas.updateLoadBalancerHealthMonitors(uuid, checks)
        return self.client.call('SoftLayer_Network_LBaaS_HealthMonitor', 'updateLoadBalancerHealthMonitors',
                                uuid, checks)

    def get_lbaas_uuid_id(self, identifier):
        """Gets a LBaaS uuid, id. Since sometimes you need one or the other.

        :param identifier: either the LB Id, UUID or Name, this function will return UUI and LB Id.
        :return (uuid, id):
        """
        mask = "mask[id,uuid]"
        if isinstance(identifier, int) or identifier.isdigit():
            this_lb = self.lbaas.getObject(id=identifier, mask=mask)
        elif len(identifier) == 36 and utils.UUID_RE.match(identifier):
            this_lb = self.lbaas.getLoadBalancer(identifier, mask=mask)
        else:
            this_lb = self.get_lbaas_by_name(identifier, mask=mask)

        return this_lb.get('uuid'), this_lb.get('id')

    def get_lbaas_by_name(self, name, mask=None):
        """Gets a LBaaS by name.

        :param name: Name of the LBaaS instance
        :param mask:
        :returns: SoftLayer_Network_LBaaS_LoadBalancer.
        """
        object_filter = {'name': {'operation': name}}
        this_lbs = self.lbaas.getAllObjects(filter=object_filter, mask=mask)
        if not this_lbs:
            raise exceptions.SoftLayerError("Unable to find LBaaS with name: {}".format(name))

        return this_lbs[0]

    def delete_lb_member(self, identifier, member_id):
        """Removes a member from a LBaaS instance

        https://sldn.softlayer.com/reference/services/SoftLayer_Network_LBaaS_Member/deleteLoadBalancerMembers/
        :param identifier: UUID of the LBaaS instance
        :param member_id: Member UUID to remove.
        """
        return self.client.call('SoftLayer_Network_LBaaS_Member', 'deleteLoadBalancerMembers',
                                identifier, [member_id])

    def add_lb_member(self, identifier, service_info):
        """Adds a member to a LBaaS instance

        https://sldn.softlayer.com/reference/services/SoftLayer_Network_LBaaS_Member/deleteLoadBalancerMembers/
        :param identifier: UUID of the LBaaS instance
        :param service_info: datatypes/SoftLayer_Network_LBaaS_LoadBalancerServerInstanceInfo
        """

        return self.client.call('SoftLayer_Network_LBaaS_Member', 'addLoadBalancerMembers',
                                identifier, [service_info])

    def add_lb_listener(self, identifier, listener):
        """Adds or update a listener to a LBaaS instance

        When using this to update a listener, just include the 'listenerUuid' in the listener object
        See the following for listener configuration options
        https://sldn.softlayer.com/reference/datatypes/SoftLayer_Network_LBaaS_LoadBalancerProtocolConfiguration/

        :param identifier: UUID of the LBaaS instance
        :param listener: Object with all listener configurations
        """

        return self.client.call('SoftLayer_Network_LBaaS_Listener', 'updateLoadBalancerProtocols',
                                identifier, [listener])

    def add_lb_l7_pool(self, identifier, pool, members, health, session):
        """Creates a new l7 pool for a LBaaS instance

        - https://sldn.softlayer.com/reference/services/SoftLayer_Network_LBaaS_L7Pool/createL7Pool/
        - https://cloud.ibm.com/docs/infrastructure/loadbalancer-service?topic=loadbalancer-service-api-reference

        :param identifier: UUID of the LBaaS instance
        :param pool SoftLayer_Network_LBaaS_L7Pool: Description of the pool
        :param members SoftLayer_Network_LBaaS_L7Member[]: Array of servers with their address, port, weight
        :param monitor SoftLayer_Network_LBaaS_L7HealthMonitor: A health monitor
        :param session  SoftLayer_Network_LBaaS_L7SessionAffinity: Weather to use affinity
        """

        return self.client.call('SoftLayer_Network_LBaaS_L7Pool', 'createL7Pool',
                                identifier, pool, members, health, session)

    def del_lb_l7_pool(self, identifier):
        """Deletes a l7 pool

        :param identifier: Id of the L7Pool
        """
        return self.client.call('SoftLayer_Network_LBaaS_L7Pool', 'deleteObject', id=identifier)

    def remove_lb_listener(self, identifier, listener):
        """Removes a listener to a LBaaS instance

        :param identifier: UUID of the LBaaS instance
        :param listener: UUID of the Listner to be removed.
        """

        return self.client.call('SoftLayer_Network_LBaaS_Listener', 'deleteLoadBalancerProtocols',
                                identifier, [listener])

    def order_lbaas(self, datacenter, name, desc, protocols, subnet_id, public=False, verify=False):
        """Allows to order a Load Balancer

        :param datacenter: Shortname for the SoftLayer datacenter to order in.
        :param name: Identifier for the new LB.
        :param desc: Optional description for the lb.
        :param protocols:  https://sldn.softlayer.com/reference/datatypes/SoftLayer_Network_LBaaS_Listener/
        :param subnet_id: Id of the subnet for this new LB to live on.
        :param public: Use Public side for the backend.
        :param verify: Don't actually order if True.
        """
        order_mgr = ordering.OrderingManager(self.client)

        package = order_mgr.get_package_by_key(self.package_keyname, mask='mask[id,keyName,itemPrices]')

        prices = []
        for price in package.get('itemPrices'):
            if not price.get('locationGroupId', False):
                prices.append(price.get('id'))

        # Build the configuration of the order
        order_data = {
            'complexType': 'SoftLayer_Container_Product_Order_Network_LoadBalancer_AsAService',
            'name': name,
            'description': desc,
            'location': datacenter,
            'packageId': package.get('id'),
            'useHourlyPricing': True,  # Required since LBaaS is an hourly service
            'prices': [{'id': price_id} for price_id in prices],
            'protocolConfigurations': protocols,
            'subnets': [{'id': subnet_id}],
            'isPublic': public
        }

        if verify:
            response = self.client['Product_Order'].verifyOrder(order_data)
        else:
            response = self.client['Product_Order'].placeOrder(order_data)
        return response

    def lbaas_order_options(self):
        """Gets the options to order a LBaaS instance."""
        _filter = {'keyName': {'operation': self.package_keyname}}
        mask = "mask[id,keyName,name,items[prices],regions[location[location[groups]]]]"
        package = self.client.call('SoftLayer_Product_Package', 'getAllObjects', filter=_filter, mask=mask)
        return package.pop()

    def cancel_lbaas(self, uuid):
        """Cancels a LBaaS instance.

        https://sldn.softlayer.com/reference/services/SoftLayer_Network_LBaaS_LoadBalancer/cancelLoadBalancer/
        :param uuid string: UUID of the LBaaS instance to cancel
        """

        return self.lbaas.cancelLoadBalancer(uuid)
