"""
    SoftLayer.load_balancer
    ~~~~~~~~~~~~~~~~~~~~~~~
    Load Balancer Manager/helpers

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import utils


class LoadBalancerManager(utils.IdentifierMixin, object):
    """Manages load balancers.

    :param SoftLayer.API.Client client: the API client instance
    """

    def __init__(self, client):
        self.client = client
        self.account = self.client['Account']
        self.prod_pkg = self.client['Product_Package']
        self.lb_svc = self.client['Network_Application_Delivery_Controller_'
                                  'LoadBalancer_VirtualIpAddress']

    def get_lb_pkgs(self):
        """Retrieves the local load balancer packages.

        :returns: A dictionary containing the load balancer packages
        """

        _filter = {'items': {'description':
                             utils.query_filter('*Load Balancer*')}}

        packages = self.prod_pkg.getItems(id=0, filter=_filter)
        pkgs = []
        for package in packages:
            if not package['description'].startswith('Global'):
                pkgs.append(package)
        return pkgs

    def get_hc_types(self):
        """Retrieves the health check type values.

        :returns: A dictionary containing the health check types
        """

        svc = self.client['Network_Application_Delivery_Controller_'
                          'LoadBalancer_Health_Check_Type']
        return svc.getAllObjects()

    def get_routing_methods(self):
        """Retrieves the load balancer routing methods.

        :returns: A dictionary containing the load balancer routing methods
        """

        svc = self.client['Network_Application_Delivery_Controller_'
                          'LoadBalancer_Routing_Method']
        return svc.getAllObjects()

    def get_routing_types(self):
        """Retrieves the load balancer routing types.

        :returns: A dictionary containing the load balancer routing types
        """

        svc = self.client['Network_Application_Delivery_Controller_'
                          'LoadBalancer_Routing_Type']
        return svc.getAllObjects()

    def _get_location(self, datacenter_name):
        """Returns the location of the specified datacenter.

        :param string datacenter_name: The datacenter to create
                                       the loadbalancer in

        :returns: the location id of the given datacenter
        """

        datacenters = self.client['Location'].getDataCenters()
        for datacenter in datacenters:
            if datacenter['name'] == datacenter_name:
                return datacenter['id']
        return 'FIRST_AVAILABLE'

    def cancel_lb(self, loadbal_id):
        """Cancels the specified load balancer.

        :param int loadbal_id: Load Balancer ID to be cancelled.
        """

        lb_billing = self.lb_svc.getBillingItem(id=loadbal_id)
        billing_id = lb_billing['id']
        billing_item = self.client['Billing_Item']
        return billing_item.cancelService(id=billing_id)

    def add_local_lb(self, price_item_id, datacenter):
        """Creates a local load balancer in the specified data center.

        :param int price_item_id: The price item ID for the load balancer
        :param string datacenter: The datacenter to create the loadbalancer in
        :returns: A dictionary containing the product order
        """

        product_order = {
            'complexType': 'SoftLayer_Container_Product_Order_Network_'
                           'LoadBalancer',
            'quantity': 1,
            'packageId': 0,
            "location": self._get_location(datacenter),
            'prices': [{'id': price_item_id}]
        }
        return self.client['Product_Order'].placeOrder(product_order)

    def get_local_lbs(self):
        """Returns a list of all local load balancers on the account.

        :returns: A list of all local load balancers on the current account.
        """

        mask = 'loadBalancerHardware[datacenter],ipAddress'
        return self.account.getAdcLoadBalancers(mask=mask)

    def get_local_lb(self, loadbal_id, **kwargs):
        """Returns a specified local load balancer given the id.

        :param int loadbal_id: The id of the load balancer to retrieve
        :returns: A dictionary containing the details of the load balancer
        """

        if 'mask' not in kwargs:
            kwargs['mask'] = ('loadBalancerHardware[datacenter], '
                              'ipAddress, virtualServers[serviceGroups'
                              '[routingMethod,routingType,services'
                              '[healthChecks[type], groupReferences,'
                              ' ipAddress]]]')

        return self.lb_svc.getObject(id=loadbal_id, **kwargs)

    def delete_service(self, service_id):
        """Deletes a service from the loadbal_id.

        :param int service_id: The id of the service to delete
        """

        svc = self.client['Network_Application_Delivery_Controller_'
                          'LoadBalancer_Service']

        return svc.deleteObject(id=service_id)

    def delete_service_group(self, group_id):
        """Deletes a service group from the loadbal_id.

        :param int group_id: The id of the service group to delete
        """

        svc = self.client['Network_Application_Delivery_Controller_'
                          'LoadBalancer_VirtualServer']

        return svc.deleteObject(id=group_id)

    def toggle_service_status(self, service_id):
        """Toggles the service status.

        :param int service_id: The id of the service to delete
        """

        svc = self.client['Network_Application_Delivery_Controller_'
                          'LoadBalancer_Service']
        return svc.toggleStatus(id=service_id)

    def edit_service(self, loadbal_id, service_id, ip_address_id=None,
                     port=None, enabled=None, hc_type=None, weight=None):
        """Edits an existing service properties.

        :param int loadbal_id: The id of the loadbal where the service resides
        :param int service_id: The id of the service to edit
        :param string ip_address: The ip address of the service
        :param int port: the port of the service
        :param bool enabled: enable or disable the search
        :param int hc_type: The health check type
        :param int weight: the weight to give to the service
        """

        _filter = {
            'virtualServers': {
                'serviceGroups': {
                    'services': {'id': utils.query_filter(service_id)}}}}

        mask = 'serviceGroups[services[groupReferences,healthChecks]]'

        virtual_servers = self.lb_svc.getVirtualServers(id=loadbal_id,
                                                        filter=_filter,
                                                        mask=mask)

        for service in virtual_servers[0]['serviceGroups'][0]['services']:
            if service['id'] == service_id:
                if enabled is not None:
                    service['enabled'] = int(enabled)
                if port is not None:
                    service['port'] = port
                if weight is not None:
                    service['groupReferences'][0]['weight'] = weight
                if hc_type is not None:
                    service['healthChecks'][0]['healthCheckTypeId'] = hc_type
                if ip_address_id is not None:
                    service['ipAddressId'] = ip_address_id

        template = {'virtualServers': list(virtual_servers)}

        load_balancer = self.lb_svc.editObject(template, id=loadbal_id)
        return load_balancer

    def add_service(self, loadbal_id, service_group_id, ip_address_id,
                    port=80, enabled=True, hc_type=21, weight=1):
        """Adds a new service to the service group.

        :param int loadbal_id: The id of the loadbal where the service resides
        :param int service_group_id: The group to add the service to
        :param int ip_address id: The ip address ID of the service
        :param int port: the port of the service
        :param bool enabled: Enable or disable the service
        :param int hc_type: The health check type
        :param int weight: the weight to give to the service
        """
        kwargs = utils.NestedDict({})
        kwargs['mask'] = ('virtualServers['
                          'serviceGroups[services[groupReferences]]]')

        load_balancer = self.lb_svc.getObject(id=loadbal_id, **kwargs)
        virtual_servers = load_balancer['virtualServers']
        for virtual_server in virtual_servers:
            if virtual_server['id'] == service_group_id:
                service_template = {
                    'enabled': int(enabled),
                    'port': port,
                    'ipAddressId': ip_address_id,
                    'healthChecks': [
                        {
                            'healthCheckTypeId': hc_type
                        }
                    ],
                    'groupReferences': [
                        {
                            'weight': weight
                        }
                    ]
                }
                services = virtual_server['serviceGroups'][0]['services']
                services.append(service_template)

        return self.lb_svc.editObject(load_balancer, id=loadbal_id)

    def add_service_group(self, lb_id, allocation=100, port=80,
                          routing_type=2, routing_method=10):
        """Adds a new service group to the load balancer.

        :param int loadbal_id: The id of the loadbal where the service resides
        :param int allocation: percent of connections to allocate toward the
                               group
        :param int port: the port of the service group
        :param int routing_type: the routing type to set on the service group
        :param int routing_method: The routing method to set on the group
        """

        mask = 'virtualServers[serviceGroups[services[groupReferences]]]'
        load_balancer = self.lb_svc.getObject(id=lb_id, mask=mask)
        service_template = {
            'port': port,
            'allocation': allocation,
            'serviceGroups': [
                {
                    'routingTypeId': routing_type,
                    'routingMethodId': routing_method
                }
            ]
        }

        load_balancer['virtualServers'].append(service_template)
        return self.lb_svc.editObject(load_balancer, id=lb_id)

    def edit_service_group(self, loadbal_id, group_id, allocation=None,
                           port=None, routing_type=None, routing_method=None):
        """Edit an existing service group.

        :param int loadbal_id: The id of the loadbal where the service resides
        :param int group_id: The id of the service group
        :param int allocation: the % of connections to allocate to the group
        :param int port: the port of the service group
        :param int routing_type: the routing type to set on the service group
        :param int routing_method: The routing method to set on the group
        """

        mask = 'virtualServers[serviceGroups[services[groupReferences]]]'

        load_balancer = self.lb_svc.getObject(id=loadbal_id, mask=mask)
        virtual_servers = load_balancer['virtualServers']

        for virtual_server in virtual_servers:
            if virtual_server['id'] == group_id:
                service_group = virtual_server['serviceGroups'][0]
                if allocation is not None:
                    virtual_server['allocation'] = allocation
                if port is not None:
                    virtual_server['port'] = port
                if routing_type is not None:
                    service_group['routingTypeId'] = routing_type
                if routing_method is not None:
                    service_group['routingMethodId'] = routing_method
                break

        return self.lb_svc.editObject(load_balancer, id=loadbal_id)

    def reset_service_group(self, loadbal_id, group_id):
        """Resets all the connections on the service group.

        :param int loadbal_id: The id of the loadbal
        :param int group_id: The id of the service group to reset
        """

        _filter = {'virtualServers': {'id': utils.query_filter(group_id)}}
        virtual_servers = self.lb_svc.getVirtualServers(id=loadbal_id,
                                                        filter=_filter,
                                                        mask='serviceGroups')
        actual_id = virtual_servers[0]['serviceGroups'][0]['id']

        svc = self.client['Network_Application_Delivery_Controller'
                          '_LoadBalancer_Service_Group']
        return svc.kickAllConnections(id=actual_id)
