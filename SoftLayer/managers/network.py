"""
    SoftLayer.network
    ~~~~~~~~~~~~~~~~~
    Network Manager/helpers

    :license: MIT, see LICENSE for more details.
"""
import collections
import json
import logging

from SoftLayer.decoration import retry

from SoftLayer import exceptions
from SoftLayer import utils

from SoftLayer.managers import event_log

LOGGER = logging.getLogger(__name__)

# pylint: disable=too-many-public-methods

DEFAULT_SUBNET_MASK = ','.join(['hardware',
                                'datacenter',
                                'networkVlanId',
                                'ipAddressCount',
                                'virtualGuests',
                                'id',
                                'networkIdentifier',
                                'cidr',
                                'subnetType',
                                'gateway',
                                'broadcastAddress',
                                'usableIpAddressCount',
                                'note',
                                'tagReferences[tag]',
                                'networkVlan[id,networkSpace]'])
DEFAULT_VLAN_MASK = ','.join([
    'firewallInterfaces',
    'hardwareCount',
    'primaryRouter[id, fullyQualifiedDomainName, datacenter]',
    'subnetCount',
    'totalPrimaryIpAddressCount',
    'virtualGuestCount',
    'networkSpace',
    'networkVlanFirewall[id,fullyQualifiedDomainName,primaryIpAddress]',
    'attachedNetworkGateway[id,name,networkFirewall]',
])
DEFAULT_GET_VLAN_MASK = ','.join([
    'firewallInterfaces',
    'primaryRouter[id, fullyQualifiedDomainName, datacenter]',
    'totalPrimaryIpAddressCount',
    'networkSpace',
    'billingItem',
    'hardware',
    'subnets',
    'virtualGuests',
    'networkVlanFirewall[id,fullyQualifiedDomainName,primaryIpAddress]',
    'attachedNetworkGateway[id,name,networkFirewall]',
])


class NetworkManager(object):
    """Manage SoftLayer network objects: VLANs, subnets and IPs

    See product information here: https://www.ibm.com/cloud/network

    :param SoftLayer.API.BaseClient client: the client instance

    """

    def __init__(self, client):
        self.client = client
        self.account = client['Account']
        self.vlan = client['Network_Vlan']
        self.subnet = client['Network_Subnet']
        self.network_storage = self.client['Network_Storage']
        self.security_group = self.client['Network_SecurityGroup']

    def add_global_ip(self, version=4, test_order=False):
        """Adds a global IP address to the account.

        :param int version: Specifies whether this is IPv4 or IPv6
        :param bool test_order: If true, this will only verify the order.
        """
        # This method is here to improve the public interface from a user's
        # perspective since ordering a single global IP through the subnet
        # interface is not intuitive.
        return self.add_subnet('global', version=version,
                               test_order=test_order)

    def add_securitygroup_rule(self, group_id, remote_ip=None,
                               remote_group=None, direction=None,
                               ethertype=None, port_max=None,
                               port_min=None, protocol=None):
        """Add a rule to a security group

        :param int group_id: The ID of the security group to add this rule to
        :param str remote_ip: The remote IP or CIDR to enforce the rule on
        :param int remote_group: The remote security group ID to enforce
                                 the rule on
        :param str direction: The direction to enforce (egress or ingress)
        :param str ethertype: The ethertype to enforce (IPv4 or IPv6)
        :param int port_max: The upper port bound to enforce
                             (icmp code if the protocol is icmp)
        :param int port_min: The lower port bound to enforce
                             (icmp type if the protocol is icmp)
        :param str protocol: The protocol to enforce (icmp, udp, tcp)
        """
        rule = {'direction': direction}
        if ethertype is not None:
            rule['ethertype'] = ethertype
        if port_max is not None:
            rule['portRangeMax'] = port_max
        if port_min is not None:
            rule['portRangeMin'] = port_min
        if protocol is not None:
            rule['protocol'] = protocol
        if remote_ip is not None:
            rule['remoteIp'] = remote_ip
        if remote_group is not None:
            rule['remoteGroupId'] = remote_group
        return self.add_securitygroup_rules(group_id, [rule])

    def add_securitygroup_rules(self, group_id, rules):
        """Add rules to a security group

        :param int group_id: The ID of the security group to add the rules to
        :param list rules: The list of rule dictionaries to add
        """
        if not isinstance(rules, list):
            raise TypeError("The rules provided must be a list of dictionaries")
        return self.security_group.addRules(rules, id=group_id)

    def add_subnet(self, subnet_type, quantity=None, endpoint_id=None, version=4,
                   test_order=False):
        """Orders a new subnet

        :param str subnet_type: Type of subnet to add: private, public, global,static
        :param int quantity: Number of IPs in the subnet
        :param int endpoint_id: id for the subnet to be placed into
        :param int version: 4 for IPv4, 6 for IPv6
        :param bool test_order: If true, this will only verify the order.
        """
        package = self.client['Product_Package']
        category = 'sov_sec_ip_addresses_priv'
        desc = ''
        if version == 4:
            if subnet_type == 'global':
                quantity = 0
                category = "global_ipv4"
            elif subnet_type == 'public':
                category = "sov_sec_ip_addresses_pub"
            elif subnet_type == 'static':
                category = "static_sec_ip_addresses"
        else:
            category = 'static_ipv6_addresses'
            if subnet_type == 'global':
                quantity = 0
                category = 'global_ipv6'
                desc = 'Global'
            elif subnet_type == 'public':
                desc = 'Portable'
            elif subnet_type == 'static':
                desc = 'Static'

        # In the API, every non-server item is contained within package ID 0.
        # This means that we need to get all of the items and loop through them
        # looking for the items we need based upon the category, quantity, and
        # item description.
        price_id = None
        quantity_str = str(quantity)
        package_items = package.getItems(id=0, mask='mask[prices[packageReferences[package[keyName]]]]')
        for item in package_items:
            category_code = utils.lookup(item, 'itemCategory', 'categoryCode')
            if all([category_code == category,
                    item.get('capacity') == quantity_str,
                    version == 4 or (version == 6 and
                                     desc in item['description'])]):
                price_id = self.get_subnet_item_price(item, subnet_type, version)
                break

        order = {
            'packageId': 0,
            'prices': [{'id': price_id}],
            'quantity': 1,
            # This is necessary in order for the XML-RPC endpoint to select the
            # correct order container
            'complexType': 'SoftLayer_Container_Product_Order_Network_Subnet',
        }
        if subnet_type == 'static':
            order['endPointIpAddressId'] = endpoint_id
        elif subnet_type != 'global' and subnet_type != 'static':
            order['endPointVlanId'] = endpoint_id

        if test_order:
            return self.client['Product_Order'].verifyOrder(order)
        else:
            return self.client['Product_Order'].placeOrder(order)

    @staticmethod
    def get_subnet_item_price(item, subnet_type, version):
        """Get the subnet specific item price id.

        :param version: 4 for IPv4, 6 for IPv6.
        :param subnet_type: Type of subnet to add: private, public, global,static.
        :param item: Subnet item.
        """
        price_id = None
        if version == 4 and subnet_type == 'static':
            for item_price in item['prices']:
                for package_reference in item_price['packageReferences']:
                    if subnet_type.upper() in package_reference['package']['keyName']:
                        price_id = item_price['id']
        else:
            price_id = item['prices'][0]['id']
        return price_id

    def assign_global_ip(self, global_ip_id, target):
        """Assigns a global IP address to a specified target.

        :param int global_ip_id: The ID of the global IP being assigned
        :param string target: The IP address to assign
        """
        return self.client['Network_Subnet_IpAddress_Global'].route(
            target, id=global_ip_id)

    def attach_securitygroup_component(self, group_id, component_id):
        """Attaches a network component to a security group.

        :param int group_id: The ID of the security group
        :param int component_id: The ID of the network component to attach
        """
        return self.attach_securitygroup_components(group_id,
                                                    [component_id])

    def attach_securitygroup_components(self, group_id, component_ids):
        """Attaches network components to a security group.

        :param int group_id: The ID of the security group
        :param list component_ids: The IDs of the network components to attach
        """
        return self.security_group.attachNetworkComponents(component_ids,
                                                           id=group_id)

    def cancel_global_ip(self, global_ip_id):
        """Cancels the specified global IP address.

        :param int id: The ID of the global IP to be cancelled.
        """
        service = self.client['Network_Subnet_IpAddress_Global']
        ip_address = service.getObject(id=global_ip_id, mask='billingItem')
        billing_id = ip_address['billingItem']['id']

        return self.client['Billing_Item'].cancelService(id=billing_id)

    def cancel_subnet(self, subnet_id):
        """Cancels the specified subnet.

        :param int subnet_id: The ID of the subnet to be cancelled.
        """
        subnet = self.get_subnet(subnet_id, mask='id, billingItem.id')
        if "billingItem" not in subnet:
            raise exceptions.SoftLayerError("subnet %s can not be cancelled"
                                            " " % subnet_id)
        billing_id = subnet['billingItem']['id']
        return self.client['Billing_Item'].cancelService(id=billing_id)

    def set_tags_subnet(self, subnet_id, tags):
        """Tag a subnet by passing in one or more tags separated by a comma.

        :param int subnet_id: The ID of the subnet.
        :param string tags:	Comma separated list of tags.
        """
        return self.subnet.setTags(tags, id=subnet_id)

    def edit_note_subnet(self, subnet_id, note):
        """Edit the note for this subnet.

        :param int subnet_id: The ID of the subnet.
        :param string note:	The note.
        """
        return self.subnet.editNote(note, id=subnet_id)

    def create_securitygroup(self, name=None, description=None):
        """Creates a security group.

        :param string name: The name of the security group
        :param string description: The description of the security group
        """

        create_dict = {'name': name, 'description': description}
        return self.security_group.createObject(create_dict)

    def delete_securitygroup(self, group_id):
        """Deletes the specified security group.

        :param int group_id: The ID of the security group
        """
        return self.security_group.deleteObject(id=group_id)

    def detach_securitygroup_component(self, group_id, component_id):
        """Detaches a network component from a security group.

        :param int group_id: The ID of the security group
        :param int component_id: The ID of the component to detach
        """
        return self.detach_securitygroup_components(group_id, [component_id])

    def detach_securitygroup_components(self, group_id, component_ids):
        """Detaches network components from a security group.

        :param int group_id: The ID of the security group
        :param list component_ids: The IDs of the network components to detach
        """
        return self.security_group.detachNetworkComponents(component_ids,
                                                           id=group_id)

    def edit_securitygroup(self, group_id, name=None, description=None):
        """Edit security group details.

        :param int group_id: The ID of the security group
        :param string name: The name of the security group
        :param string description: The description of the security group
        """
        successful = False
        obj = {}
        if name:
            obj['name'] = name
        if description:
            obj['description'] = description

        if obj:
            successful = self.security_group.editObject(obj, id=group_id)

        return successful

    def edit_securitygroup_rule(self, group_id, rule_id, remote_ip=None,
                                remote_group=None, direction=None,
                                ethertype=None, port_max=None,
                                port_min=None, protocol=None):
        """Edit a security group rule.

        :param int group_id: The ID of the security group the rule belongs to
        :param int rule_id: The ID of the rule to edit
        :param str remote_ip: The remote IP or CIDR to enforce the rule on
        :param int remote_group: The remote security group ID to enforce
                                          the rule on
        :param str direction: The direction to enforce (egress or ingress)
        :param str ethertype: The ethertype to enforce (IPv4 or IPv6)
        :param str port_max: The upper port bound to enforce
        :param str port_min: The lower port bound to enforce
        :param str protocol: The protocol to enforce (icmp, udp, tcp)
        """
        successful = False
        obj = {}
        if remote_ip is not None:
            obj['remoteIp'] = remote_ip
        if remote_group is not None:
            obj['remoteGroupId'] = remote_group
        if direction is not None:
            obj['direction'] = direction
        if ethertype is not None:
            obj['ethertype'] = ethertype
        if port_max is not None:
            obj['portRangeMax'] = port_max
        if port_min is not None:
            obj['portRangeMin'] = port_min
        if protocol is not None:
            obj['protocol'] = protocol

        if obj:
            obj['id'] = rule_id
            successful = self.security_group.editRules([obj], id=group_id)

        return successful

    def ip_lookup(self, ip_address):
        """Looks up an IP address and returns network information about it.

        :param string ip_address: An IP address. Can be IPv4 or IPv6
        :returns: A dictionary of information about the IP

        """
        obj = self.client['Network_Subnet_IpAddress']
        return obj.getByIpAddress(ip_address, mask='hardware, virtualGuest')

    def get_securitygroup(self, group_id, **kwargs):
        """Returns the information about the given security group.

        :param string id: The ID for the security group
        :returns: A diction of information about the security group
        """
        if 'mask' not in kwargs:
            kwargs['mask'] = (
                'id,'
                'name,'
                'description,'
                '''rules[id, remoteIp, remoteGroupId,
                         direction, ethertype, portRangeMin,
                         portRangeMax, protocol, createDate, modifyDate],'''
                '''networkComponentBindings[
                    networkComponent[
                        id,
                        port,
                        guest[
                            id,
                            hostname,
                            primaryBackendIpAddress,
                            primaryIpAddress
                        ]
                    ]
                ]'''
            )

        return self.security_group.getObject(id=group_id, **kwargs)

    def get_subnet(self, subnet_id, **kwargs):
        """Returns information about a single subnet.

        :param string id: Either the ID for the subnet or its network
                          identifier
        :returns: A dictionary of information about the subnet
        """
        if 'mask' not in kwargs:
            kwargs['mask'] = DEFAULT_SUBNET_MASK

        return self.subnet.getObject(id=subnet_id, **kwargs)

    def get_vlan(self, vlan_id):
        """Returns information about a single VLAN.

        :param int id: The unique identifier for the VLAN
        :returns: A dictionary containing a large amount of information about
                  the specified VLAN.

        """
        return self.vlan.getObject(id=vlan_id, mask=DEFAULT_GET_VLAN_MASK)

    def list_global_ips(self, version=None, identifier=None, **kwargs):
        """Returns a list of all global IP address records on the account.

        :param int version: Only returns IPs of this version (4 or 6)
        :param string identifier: If specified, the list will only contain the
                                  global ips matching this network identifier.
        """
        if 'mask' not in kwargs:
            mask = ['destinationIpAddress[hardware, virtualGuest]',
                    'ipAddress']
            kwargs['mask'] = ','.join(mask)

        _filter = utils.NestedDict({})

        if version:
            ver = utils.query_filter(version)
            _filter['globalIpRecords']['ipAddress']['subnet']['version'] = ver

        if identifier:
            subnet_filter = _filter['globalIpRecords']['ipAddress']['subnet']
            subnet_filter['networkIdentifier'] = utils.query_filter(identifier)

        kwargs['filter'] = _filter.to_dict()
        return self.account.getGlobalIpRecords(**kwargs)

    def list_subnets(self, identifier=None, datacenter=None, version=0,
                     subnet_type=None, network_space=None, **kwargs):
        """Display a list of all subnets on the account.

        This provides a quick overview of all subnets including information
        about data center residence and the number of devices attached.

        :param string identifier: If specified, the list will only contain the
                                    subnet matching this network identifier.
        :param string datacenter: If specified, the list will only contain
                                    subnets in the specified data center.
        :param int version: Only returns subnets of this version (4 or 6).
        :param string subnet_type: If specified, it will only returns subnets
                                     of this type.
        :param string network_space: If specified, it will only returns subnets
                                       with the given address space label.
        :param dict \\*\\*kwargs: response-level options (mask, limit, etc.)
        """
        if 'mask' not in kwargs:
            kwargs['mask'] = DEFAULT_SUBNET_MASK

        _filter = utils.NestedDict(kwargs.get('filter') or {})

        if identifier:
            _filter['subnets']['networkIdentifier'] = (
                utils.query_filter(identifier))
        if datacenter:
            _filter['subnets']['datacenter']['name'] = (
                utils.query_filter(datacenter))
        if version:
            _filter['subnets']['version'] = utils.query_filter(version)
        if subnet_type:
            _filter['subnets']['subnetType'] = utils.query_filter(subnet_type)
        else:
            # This filters out global IPs from the subnet listing.
            _filter['subnets']['subnetType'] = {'operation': '!= GLOBAL_IP'}
        if network_space:
            _filter['subnets']['networkVlan']['networkSpace'] = (
                utils.query_filter(network_space))

        kwargs['filter'] = _filter.to_dict()
        kwargs['iter'] = True
        return self.client.call('Account', 'getSubnets', **kwargs)

    def list_vlans(self, datacenter=None, vlan_number=None, name=None, **kwargs):
        """Display a list of all VLANs on the account.

        This provides a quick overview of all VLANs including information about
        data center residence and the number of devices attached.

        :param string datacenter: If specified, the list will only contain
                                    VLANs in the specified data center.
        :param int vlan_number: If specified, the list will only contain the
                                  VLAN matching this VLAN number.
        :param int name: If specified, the list will only contain the
                                  VLAN matching this VLAN name.
        :param dict \\*\\*kwargs: response-level options (mask, limit, etc.)

        """
        _filter = utils.NestedDict(kwargs.get('filter') or {})

        if vlan_number:
            _filter['networkVlans']['vlanNumber'] = (
                utils.query_filter(vlan_number))

        if name:
            _filter['networkVlans']['name'] = utils.query_filter(name)

        if datacenter:
            _filter['networkVlans']['primaryRouter']['datacenter']['name'] = (
                utils.query_filter(datacenter))

        kwargs['filter'] = _filter.to_dict()

        if 'mask' not in kwargs:
            kwargs['mask'] = DEFAULT_VLAN_MASK

        kwargs['iter'] = True
        return self.account.getNetworkVlans(**kwargs)

    def list_securitygroups(self, **kwargs):
        """List security groups."""
        kwargs['iter'] = True
        return self.security_group.getAllObjects(**kwargs)

    def list_securitygroup_rules(self, group_id):
        """List security group rules associated with a security group.

        :param int group_id: The security group to list rules for
        """
        return self.security_group.getRules(id=group_id, iter=True)

    def remove_securitygroup_rule(self, group_id, rule_id):
        """Remove a rule from a security group.

        :param int group_id: The ID of the security group
        :param int rule_id: The ID of the rule to remove
        """
        return self.remove_securitygroup_rules(group_id, [rule_id])

    def remove_securitygroup_rules(self, group_id, rules):
        """Remove rules from a security group.

        :param int group_id: The ID of the security group
        :param list rules: The list of IDs to remove
        """
        return self.security_group.removeRules(rules, id=group_id)

    def get_event_logs_by_request_id(self, request_id):
        """Gets all event logs by the given request id

        :param string request_id: The request id we want to filter on
        """

        # Get all relevant event logs
        unfiltered_logs = self._get_cci_event_logs() + self._get_security_group_event_logs()

        # Grab only those that have the specific request id
        filtered_logs = []

        for unfiltered_log in unfiltered_logs:
            try:
                metadata = json.loads(unfiltered_log['metaData'])
                if 'requestId' in metadata:
                    if metadata['requestId'] == request_id:
                        filtered_logs.append(unfiltered_log)
            except ValueError:
                continue

        return filtered_logs

    def _get_cci_event_logs(self):
        # Load the event log manager
        event_log_mgr = event_log.EventLogManager(self.client)

        # Get CCI Event Logs
        _filter = event_log_mgr.build_filter(obj_type='CCI')
        return event_log_mgr.get_event_logs(request_filter=_filter)

    def _get_security_group_event_logs(self):
        # Load the event log manager
        event_log_mgr = event_log.EventLogManager(self.client)

        # Get CCI Event Logs
        _filter = event_log_mgr.build_filter(obj_type='Security Group')
        return event_log_mgr.get_event_logs(request_filter=_filter)

    def resolve_global_ip_ids(self, identifier):
        """Resolve global ip ids."""
        return utils.resolve_ids(identifier,
                                 [self._list_global_ips_by_identifier])

    def resolve_subnet_ids(self, identifier):
        """Resolve subnet ids."""
        return utils.resolve_ids(identifier,
                                 [self._list_subnets_by_identifier])

    def resolve_vlan_ids(self, identifier):
        """Resolve VLAN ids."""
        return utils.resolve_ids(identifier, [self._list_vlans_by_name])

    def summary_by_datacenter(self):
        """Summary of the networks on the account, grouped by data center.

        The resultant dictionary is primarily useful for statistical purposes.
        It contains count information rather than raw data. If you want raw
        information, see the :func:`list_vlans` method instead.

        :returns: A dictionary keyed by data center with the data containing a
                  set of counts for subnets, hardware, virtual servers, and
                  other objects residing within that data center.

        """
        datacenters = collections.defaultdict(lambda: {
            'hardware_count': 0,
            'public_ip_count': 0,
            'subnet_count': 0,
            'virtual_guest_count': 0,
            'vlan_count': 0,
        })

        for vlan in self.list_vlans():
            name = utils.lookup(vlan, 'primaryRouter', 'datacenter', 'name')

            datacenters[name]['vlan_count'] += 1
            datacenters[name]['public_ip_count'] += (
                vlan['totalPrimaryIpAddressCount'])
            datacenters[name]['subnet_count'] += vlan['subnetCount']

            # NOTE(kmcdonald): Only count hardware/guests once
            if vlan.get('networkSpace') == 'PRIVATE':
                datacenters[name]['hardware_count'] += (
                    vlan['hardwareCount'])
                datacenters[name]['virtual_guest_count'] += (
                    vlan['virtualGuestCount'])

        return dict(datacenters)

    def unassign_global_ip(self, global_ip_id):
        """Unassigns a global IP address from a target.

        :param int id: The ID of the global IP being unassigned
        """
        return self.client['Network_Subnet_IpAddress_Global'].unroute(
            id=global_ip_id)

    def _list_global_ips_by_identifier(self, identifier):
        """Returns a list of IDs of the global IP matching the identifier.

        :param string identifier: The identifier to look up
        :returns: List of matching IDs
        """
        results = self.list_global_ips(identifier=identifier, mask='id')
        return [result['id'] for result in results]

    def _list_subnets_by_identifier(self, identifier):
        """Returns a list of IDs of the subnet matching the identifier.

        :param string identifier: The identifier to look up
        :returns: List of matching IDs
        """
        identifier = identifier.split('/', 1)[0]

        results = self.list_subnets(identifier=identifier, mask='id')
        return [result['id'] for result in results]

    def _list_vlans_by_name(self, name):
        """Returns a list of IDs of VLANs which match the given VLAN name.

        :param string name: a VLAN name
        :returns: List of matching IDs
        """
        results = self.list_vlans(name=name, mask='id')
        return [result['id'] for result in results]

    def get_nas_credentials(self, identifier, **kwargs):
        """Returns a list of IDs of VLANs which match the given VLAN name.

        :param integer instance_id: the instance ID
        :returns: A dictionary containing a large amount of information about
                  the specified instance.
        """
        result = self.network_storage.getObject(id=identifier, **kwargs)
        return result

    def edit(self, instance_id, name=None, note=None, tags=None):
        """Edit a vlan.

        :param integer instance_id: the instance ID to edit.
        :param string name: valid name.
        :param string note: note about this particular vlan.
        :param string tags: tags to set on the vlan as a comma separated list.
                            Use the empty string to remove all tags.
        :returns: bool -- True or an Exception
        """

        obj = {}

        if tags is not None:
            self.set_tags(tags, vlan_id=instance_id)

        if name:
            obj['name'] = name

        if note:
            obj['note'] = note

        if not obj:
            return True

        return self.vlan.editObject(obj, id=instance_id)

    @retry(logger=LOGGER)
    def set_tags(self, tags, vlan_id):
        """Sets tags on a vlan with a retry decorator

        Just calls vlan.setTags, but if it fails from an APIError will retry.
        """
        self.vlan.setTags(tags, id=vlan_id)

    def get_ip_by_address(self, ip_address):
        """get the ip address object

         :param string ip_address: the ip address to edit.
         """
        return self.client.call('SoftLayer_Network_Subnet_IpAddress', 'getByIpAddress', ip_address)

    def set_subnet_ipddress_note(self, identifier, note):
        """Set the ip address note of the subnet

         :param integer identifier: the ip address ID to edit.
          :param json note: the note to edit.
        """
        result = self.client.call('SoftLayer_Network_Subnet_IpAddress', 'editObject', note, id=identifier)
        return result

    def get_cancel_failure_reasons(self, identifier):
        """get the reasons why we cannot cancel the VLAN.

        :param integer identifier:  the instance ID
        """
        return self.vlan.getCancelFailureReasons(id=identifier)

    def cancel_item(self, identifier, cancel_immediately,
                    reason_cancel, customer_note):
        """Cancel a billing item immediately, deleting all its data.

        :param integer identifier: the instance ID to cancel
        :param string reason_cancel: reason cancel
        """
        return self.client.call('SoftLayer_Billing_Item', 'cancelItem',
                                True,
                                cancel_immediately,
                                reason_cancel,
                                customer_note,
                                id=identifier)

    def get_pods(self, datacenter=None):
        """Calls SoftLayer_Network_Pod::getAllObjects()

        returns list of all network pods and their routers.
        """
        _filter = None
        if datacenter:
            _filter = {"datacenterName": {"operation": datacenter}}

        return self.client.call('SoftLayer_Network_Pod', 'getAllObjects', filter=_filter)
