"""
    SoftLayer.vs
    ~~~~~~~~~~~~
    VS Manager/helpers

    :license: MIT, see LICENSE for more details.
"""
import datetime
import logging
import socket
import time
import warnings

from SoftLayer.decoration import retry
from SoftLayer import exceptions
from SoftLayer.exceptions import SoftLayerError
from SoftLayer.managers.hardware import _get_preset_cost
from SoftLayer.managers.hardware import get_item_price
from SoftLayer.managers import ordering
from SoftLayer import utils

LOGGER = logging.getLogger(__name__)

EXTRA_CATEGORIES = ['pri_ipv6_addresses',
                    'static_ipv6_addresses',
                    'sec_ip_addresses',
                    'trusted_platform_module',
                    'software_guard_extensions']


# pylint: disable=no-self-use,too-many-lines


class VSManager(utils.IdentifierMixin, object):
    """Manages SoftLayer Virtual Servers.

    See product information here: https://www.ibm.com/cloud/virtual-servers

    Example::

           # Initialize the VSManager.
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

    def __init__(self, client, ordering_manager=None):
        self.client = client
        self.account = client['Account']
        self.guest = client['Virtual_Guest']
        self.package_svc = client['Product_Package']
        self.storage_iscsi = client['SoftLayer_Network_Storage_Iscsi']
        self.resolvers = [self._get_ids_from_ip, self._get_ids_from_hostname]
        if ordering_manager is None:
            self.ordering_manager = ordering.OrderingManager(client)
        else:
            self.ordering_manager = ordering_manager

    @retry(logger=LOGGER)
    def list_instances(self, hourly=True, monthly=True, tags=None, cpus=None,
                       memory=None, hostname=None, domain=None,
                       local_disk=None, datacenter=None, nic_speed=None,
                       public_ip=None, private_ip=None, transient=None, **kwargs):
        """Retrieve a list of all virtual servers on the account.

        Example::

            # Print out a list of hourly instances in the DAL05 data center.

            for vsi in mgr.list_instances(hourly=True, datacenter='dal05'):
               print vsi['fullyQualifiedDomainName'], vsi['primaryIpAddress']

            # Using a custom object-mask. Will get ONLY what is specified
            object_mask = "mask[hostname,monitoringRobot[robotStatus]]"
            for vsi in mgr.list_instances(mask=object_mask,hourly=True):
                print vsi

        :param boolean hourly: include hourly instances
        :param boolean monthly: include monthly instances
        :param list tags: filter based on list of tags
        :param integer cpus: filter based on number of CPUS
        :param integer memory: filter based on amount of memory
        :param string hostname: filter based on hostname
        :param string domain: filter based on domain
        :param string local_disk: filter based on local_disk
        :param string datacenter: filter based on datacenter
        :param integer nic_speed: filter based on network speed (in MBPS)
        :param string public_ip: filter based on public ip address
        :param string private_ip: filter based on private ip address
        :param boolean transient: filter on transient or non-transient instances
        :param dict \\*\\*kwargs: response-level options (mask, limit, etc.)
        :returns: Returns a list of dictionaries representing the matching
                  virtual servers
        """
        if 'mask' not in kwargs:
            items = [
                'id',
                'globalIdentifier',
                'hostname',
                'domain',
                'fullyQualifiedDomainName',
                'primaryBackendIpAddress',
                'primaryIpAddress',
                'lastKnownPowerState.name',
                'powerState',
                'maxCpu',
                'maxMemory',
                'datacenter',
                'activeTransaction.transactionStatus[friendlyName,name]',
                'status',
            ]
            kwargs['mask'] = "mask[%s]" % ','.join(items)

        call = 'getVirtualGuests'
        if not all([hourly, monthly]):
            if hourly:
                call = 'getHourlyVirtualGuests'
            elif monthly:
                call = 'getMonthlyVirtualGuests'

        _filter = utils.NestedDict(kwargs.get('filter') or {})
        if tags:
            _filter['virtualGuests']['tagReferences']['tag']['name'] = {
                'operation': 'in',
                'options': [{'name': 'data', 'value': tags}],
            }

        if cpus:
            _filter['virtualGuests']['maxCpu'] = utils.query_filter(cpus)

        if memory:
            _filter['virtualGuests']['maxMemory'] = utils.query_filter(memory)

        if hostname:
            _filter['virtualGuests']['hostname'] = utils.query_filter(hostname)

        if domain:
            _filter['virtualGuests']['domain'] = utils.query_filter(domain)

        if local_disk is not None:
            _filter['virtualGuests']['localDiskFlag'] = (
                utils.query_filter(bool(local_disk)))

        if datacenter:
            _filter['virtualGuests']['datacenter']['name'] = (
                utils.query_filter(datacenter))

        if nic_speed:
            _filter['virtualGuests']['networkComponents']['maxSpeed'] = (
                utils.query_filter(nic_speed))

        if public_ip:
            _filter['virtualGuests']['primaryIpAddress'] = (
                utils.query_filter(public_ip))

        if private_ip:
            _filter['virtualGuests']['primaryBackendIpAddress'] = (
                utils.query_filter(private_ip))

        if transient is not None:
            _filter['virtualGuests']['transientGuestFlag'] = (
                utils.query_filter(bool(transient))
            )

        kwargs['filter'] = _filter.to_dict()
        kwargs['iter'] = True
        return self.client.call('Account', call, **kwargs)

    @retry(logger=LOGGER)
    def get_instance(self, instance_id, **kwargs):
        """Get details about a virtual server instance.

        :param integer instance_id: the instance ID
        :returns: A dictionary containing a large amount of information about
                  the specified instance.

        Example::

            # Print out instance ID 12345.
            vsi = mgr.get_instance(12345)
            print vsi

            # Print out only FQDN and primaryIP for instance 12345
            object_mask = "mask[fullyQualifiedDomainName,primaryIpAddress]"
            vsi = mgr.get_instance(12345, mask=mask)
            print vsi

        """

        if 'mask' not in kwargs:
            kwargs['mask'] = (
                'id,'
                'globalIdentifier,'
                'fullyQualifiedDomainName,'
                'hostname,'
                'domain,'
                'createDate,'
                'modifyDate,'
                'provisionDate,'
                'notes,'
                'dedicatedAccountHostOnlyFlag,'
                'transientGuestFlag,'
                'privateNetworkOnlyFlag,'
                'primaryBackendIpAddress,'
                'primaryIpAddress,'
                '''networkComponents[id, status, speed, maxSpeed, name,
                                     macAddress, primaryIpAddress, port,
                                     primarySubnet[addressSpace],
                                     securityGroupBindings[
                                        securityGroup[id, name]]],'''
                'lastKnownPowerState.name,'
                'powerState,'
                'status,'
                'maxCpu,'
                'maxMemory,'
                'datacenter,'
                'activeTransaction[id, transactionStatus[friendlyName,name]],'
                'lastTransaction[transactionStatus,modifyDate,transactionGroup[name]],'
                'lastOperatingSystemReload.id,'
                'blockDevices,'
                'blockDeviceTemplateGroup[id, name, globalIdentifier],'
                'postInstallScriptUri,'
                '''operatingSystem[passwords[username,password],
                                   softwareLicense.softwareDescription[
                                       manufacturer,name,version,
                                       referenceCode]],'''
                '''softwareComponents[
                    passwords[username,password,notes],
                    softwareLicense[softwareDescription[
                                        manufacturer,name,version,
                                        referenceCode]]],'''
                'hourlyBillingFlag,'
                'userData,'
                '''billingItem[id,nextInvoiceTotalRecurringAmount,
                               package[id,keyName],
                               children[categoryCode,nextInvoiceTotalRecurringAmount],
                               orderItem[id,
                                         order.userRecord[username],
                                         preset.keyName]],'''
                'tagReferences[id,tag[name,id]],'
                'networkVlans[id,vlanNumber,networkSpace],'
                'dedicatedHost.id,'
                'placementGroupId'
            )

        return self.guest.getObject(id=instance_id, **kwargs)

    @retry(logger=LOGGER)
    def get_create_options(self, vsi_type="PUBLIC_CLOUD_SERVER", datacenter=None):
        """Retrieves the available options for creating a VS.

        :param string vsi_type: vs keyName.
        :param string datacenter: short name, like dal09
        :returns: A dictionary of creation options.

        Example::

            # Prints out the create option dictionary
            options = mgr.get_create_options()
            print(options)
        """

        # TRANSIENT_CLOUD_SERVER
        # SUSPEND_CLOUD_SERVER
        package = self._get_package(vsi_type)

        location_group_id = None
        if datacenter:
            _filter = {"name": {"operation": datacenter}}
            _mask = "mask[priceGroups]"
            dc_details = self.client.call('SoftLayer_Location', 'getDatacenters', mask=_mask, filter=_filter, limit=1)
            if not dc_details:
                raise SoftLayerError("Unable to find a datacenter named {}".format(datacenter))
            # A DC will have several price groups, no good way to deal with this other than checking each.
            # An item should only belong to one type of price group.
            for group in dc_details[0].get('priceGroups', []):
                # We only care about SOME of the priceGroups, which all SHOULD start with `Location Group X`
                # Hopefully this never changes....
                if group.get('description').startswith('Location'):
                    location_group_id = group.get('id')

        # Locations
        locations = []
        for region in package['regions']:
            if datacenter is None or datacenter == region['location']['location']['name']:
                locations.append({
                    'name': region['location']['location']['longName'],
                    'key': region['location']['location']['name'],
                })

        operating_systems = []
        database = []
        port_speeds = []
        guest_core = []
        local_disk = []
        extras = []
        ram = []

        sizes = []
        for preset in package['activePresets'] + package['accountRestrictedActivePresets']:
            sizes.append({
                'name': preset['description'],
                'key': preset['keyName'],
                'hourlyRecurringFee': _get_preset_cost(preset, package['items'], 'hourly', location_group_id),
                'recurringFee': _get_preset_cost(preset, package['items'], 'monthly', location_group_id)
            })

        for item in package['items']:
            category = item['itemCategory']['categoryCode']
            # Operating systems
            if category == 'os':
                operating_systems.append({
                    'name': item['softwareDescription']['longDescription'],
                    'key': item['keyName'],
                    'referenceCode': item['softwareDescription']['referenceCode'],
                    'prices': get_item_price(item['prices'], location_group_id)
                })
            # database
            elif category == 'database':
                database.append({
                    'name': item['description'],
                    'key': item['keyName'],
                    'prices': get_item_price(item['prices'], location_group_id)
                })

            elif category == 'port_speed':
                port_speeds.append({
                    'name': item['description'],
                    'speed': item['capacity'],
                    'key': item['keyName'],
                    'prices': get_item_price(item['prices'], location_group_id)
                })

            elif category == 'guest_core':
                guest_core.append({
                    'name': item['description'],
                    'capacity': item['capacity'],
                    'key': item['keyName'],
                    'prices': get_item_price(item['prices'], location_group_id)
                })

            elif category == 'ram':
                ram.append({
                    'name': item['description'],
                    'capacity': item['capacity'],
                    'key': item['keyName'],
                    'prices': get_item_price(item['prices'], location_group_id)
                })

            elif category.__contains__('guest_disk'):
                local_disk.append({
                    'name': item['description'],
                    'capacity': item['capacity'],
                    'key': item['keyName'],
                    'disk': category,
                    'prices': get_item_price(item['prices'], location_group_id)
                })
            # Extras
            elif category in EXTRA_CATEGORIES:
                extras.append({
                    'name': item['description'],
                    'key': item['keyName'],
                    'prices': get_item_price(item['prices'], location_group_id)
                })

        return {
            'locations': locations,
            'ram': ram,
            'database': database,
            'operating_systems': operating_systems,
            'guest_core': guest_core,
            'port_speed': port_speeds,
            'guest_disk': local_disk,
            'sizes': sizes,
            'extras': extras,
        }

    @retry(logger=LOGGER)
    def _get_package(self, package_keyname):
        """Get the package related to simple vs ordering.

        :param string package_keyname: Virtual Server package keyName.
        """
        items_mask = 'mask[id,keyName,capacity,description,attributes[id,attributeTypeKeyName],' \
                     'itemCategory[id,categoryCode],softwareDescription[id,referenceCode,longDescription],' \
                     'prices[categories]]'
        # The preset prices list will only have default prices. The prices->item->prices will have location specific
        presets_mask = 'mask[prices]'
        region_mask = 'location[location[priceGroups]]'
        package = {'items': [], 'activePresets': [], 'accountRestrictedActivePresets': [], 'regions': []}
        package_info = self.ordering_manager.get_package_by_key(package_keyname, mask="mask[id]")

        package['items'] = self.client.call('SoftLayer_Product_Package', 'getItems',
                                            id=package_info.get('id'), mask=items_mask)
        package['activePresets'] = self.client.call('SoftLayer_Product_Package', 'getActivePresets',
                                                    id=package_info.get('id'), mask=presets_mask)
        package['accountRestrictedActivePresets'] = self.client.call('SoftLayer_Product_Package',
                                                                     'getAccountRestrictedActivePresets',
                                                                     id=package_info.get('id'), mask=presets_mask)
        package['regions'] = self.client.call('SoftLayer_Product_Package', 'getRegions',
                                              id=package_info.get('id'), mask=region_mask)
        return package

    def cancel_instance(self, instance_id):
        """Cancel an instance immediately, deleting all its data.

        :param integer instance_id: the instance ID to cancel

        Example::

            # Cancels instance 12345
            mgr.cancel_instance(12345)

        """
        return self.guest.deleteObject(id=instance_id)

    def reload_instance(self, instance_id,
                        post_uri=None,
                        ssh_keys=None,
                        image_id=None):
        """Perform an OS reload of an instance.

        :param integer instance_id: the instance ID to reload
        :param string post_url: The URI of the post-install script to run
                                after reload
        :param list ssh_keys: The SSH keys to add to the root user
        :param int image_id: The GUID of the image to load onto the server

        .. warning::
            This will reformat the primary drive.
            Post-provision script MUST be HTTPS for it to be executed.

        Example::

           # Reload instance ID 12345 then run a custom post-provision script.
           # Post-provision script MUST be HTTPS for it to be executed.
           post_uri = 'https://somehost.com/bootstrap.sh'
           vsi = mgr.reload_instance(12345, post_uri=post_url)

        """
        config = {}

        if post_uri:
            config['customProvisionScriptUri'] = post_uri

        if ssh_keys:
            config['sshKeyIds'] = list(ssh_keys)

        if image_id:
            config['imageTemplateId'] = image_id

        return self.client.call('Virtual_Guest', 'reloadOperatingSystem',
                                'FORCE', config, id=instance_id)

    def _generate_create_dict(
            self, cpus=None, memory=None, hourly=True,
            hostname=None, domain=None, local_disk=True,
            datacenter=None, os_code=None, image_id=None,
            dedicated=False, public_vlan=None, private_vlan=None,
            private_subnet=None, public_subnet=None,
            userdata=None, nic_speed=None, disks=None, post_uri=None,
            private=False, ssh_keys=None, public_security_groups=None,
            private_security_groups=None, boot_mode=None, transient=False, **kwargs):
        """Returns a dict appropriate to pass into Virtual_Guest::createObject

            See :func:`create_instance` for a list of available options.
        """
        required = [hostname, domain]

        flavor = kwargs.get('flavor', None)
        host_id = kwargs.get('host_id', None)

        mutually_exclusive = [
            {'os_code': os_code, 'image_id': image_id},
            {'cpu': cpus, 'flavor': flavor},
            {'memory': memory, 'flavor': flavor},
            {'flavor': flavor, 'dedicated': dedicated},
            {'flavor': flavor, 'host_id': host_id}
        ]

        if not all(required):
            raise ValueError("hostname, and domain are required")

        for mu_ex in mutually_exclusive:
            if all(mu_ex.values()):
                raise ValueError(
                    'Can only specify one of: %s' % (','.join(mu_ex.keys())))

        data = {
            "startCpus": cpus,
            "maxMemory": memory,
            "hostname": hostname,
            "domain": domain,
            "localDiskFlag": local_disk,
            "hourlyBillingFlag": hourly,
            "supplementalCreateObjectOptions": {
                "bootMode": boot_mode
            }
        }

        if flavor:
            data["supplementalCreateObjectOptions"]["flavorKeyName"] = flavor

        if dedicated and not host_id:
            data["dedicatedAccountHostOnlyFlag"] = dedicated

        if host_id:
            data["dedicatedHost"] = {"id": host_id}

        if private:
            data['privateNetworkOnlyFlag'] = private

        if transient:
            data['transientGuestFlag'] = transient

        if image_id:
            data["blockDeviceTemplateGroup"] = {"globalIdentifier": image_id}
        elif os_code:
            data["operatingSystemReferenceCode"] = os_code

        if datacenter:
            data["datacenter"] = {"name": datacenter}

        network_components = self._create_network_components(public_vlan, private_vlan,
                                                             private_subnet, public_subnet,
                                                             kwargs.get('private_router'),
                                                             kwargs.get('public_router'))
        data.update(network_components)

        if public_security_groups:
            secgroups = [{'securityGroup': {'id': int(sg)}}
                         for sg in public_security_groups]
            pnc = data.get('primaryNetworkComponent', {})
            pnc['securityGroupBindings'] = secgroups
            data.update({'primaryNetworkComponent': pnc})

        if private_security_groups:
            secgroups = [{'securityGroup': {'id': int(sg)}}
                         for sg in private_security_groups]
            pbnc = data.get('primaryBackendNetworkComponent', {})
            pbnc['securityGroupBindings'] = secgroups
            data.update({'primaryBackendNetworkComponent': pbnc})

        if userdata:
            data['userData'] = [{'value': userdata}]

        if nic_speed:
            data['networkComponents'] = [{'maxSpeed': nic_speed}]

        if disks:
            data['blockDevices'] = [
                {"device": "0", "diskImage": {"capacity": disks[0]}}
            ]

            for dev_id, disk in enumerate(disks[1:], start=2):
                data['blockDevices'].append(
                    {
                        "device": str(dev_id),
                        "diskImage": {"capacity": disk}
                    }
                )

        if post_uri:
            data['postInstallScriptUri'] = post_uri

        if ssh_keys:
            data['sshKeys'] = [{'id': key_id} for key_id in ssh_keys]

        return data

    def _create_network_components(
            self, public_vlan=None, private_vlan=None,
            private_subnet=None, public_subnet=None,
            private_router=None, public_router=None):
        parameters = {}
        if any([private_router, public_router]) and any([private_vlan, public_vlan, private_subnet, public_subnet]):
            raise exceptions.SoftLayerError("You have to select network vlan or network vlan with a subnet or "
                                            "only router, not all options")

        if private_router:
            parameters['primaryBackendNetworkComponent'] = {"router": {"id": int(private_router)}}
        if public_router:
            parameters['primaryNetworkComponent'] = {"router": {"id": int(public_router)}}
        if private_vlan:
            parameters['primaryBackendNetworkComponent'] = {"networkVlan": {"id": int(private_vlan)}}
        if public_vlan:
            parameters['primaryNetworkComponent'] = {"networkVlan": {"id": int(public_vlan)}}
        if public_subnet:
            if public_vlan is None:
                raise exceptions.SoftLayerError("You need to specify a public_vlan with public_subnet")

            parameters['primaryNetworkComponent']['networkVlan']['primarySubnet'] = {'id': int(public_subnet)}
        if private_subnet:
            if private_vlan is None:
                raise exceptions.SoftLayerError("You need to specify a private_vlan with private_subnet")

            parameters['primaryBackendNetworkComponent']['networkVlan']['primarySubnet'] = {'id': int(private_subnet)}

        return parameters

    @retry(logger=LOGGER)
    def wait_for_transaction(self, instance_id, limit, delay=10):
        """Waits on a VS transaction for the specified amount of time.

        This is really just a wrapper for wait_for_ready(pending=True).
        Provided for backwards compatibility.

        :param int instance_id: The instance ID with the pending transaction
        :param int limit: The maximum amount of time to wait.
        :param int delay: The number of seconds to sleep before checks. Defaults to 10.
        """

        return self.wait_for_ready(instance_id, limit, delay=delay, pending=True)

    def wait_for_ready(self, instance_id, limit=3600, delay=10, pending=False):
        """Determine if a VS is ready and available.

        In some cases though, that can mean that no transactions are running.
        The default arguments imply a VS is operational and ready for use by
        having network connectivity and remote access is available. Setting
        ``pending=True`` will ensure future API calls against this instance
        will not error due to pending transactions such as OS Reloads and
        cancellations.

        :param int instance_id: The instance ID with the pending transaction
        :param int limit: The maximum amount of seconds to wait.
        :param int delay: The number of seconds to sleep before checks. Defaults to 10.
        :param bool pending: Wait for pending transactions not related to
                             provisioning or reloads such as monitoring.

        Example::

            # Will return once vsi 12345 is ready, or after 10 checks
            ready = mgr.wait_for_ready(12345, 10)
        """
        now = time.time()
        until = now + limit
        mask = "mask[id, lastOperatingSystemReload[id], activeTransaction, provisionDate]"

        while now <= until:
            instance = self.get_instance(instance_id, mask=mask)
            if utils.is_ready(instance, pending):
                return True
            transaction = utils.lookup(instance, 'activeTransaction', 'transactionStatus', 'friendlyName')
            snooze = min(delay, until - now)
            LOGGER.info("%s - %d not ready. Auto retry in %ds", transaction, instance_id, snooze)
            time.sleep(snooze)
            now = time.time()

        LOGGER.info("Waiting for %d expired.", instance_id)
        return False

    def verify_create_instance(self, **kwargs):
        """Verifies an instance creation command.

        Without actually placing an order.
        See :func:`create_instance` for a list of available options.

        Example::

            new_vsi = {
                'domain': u'test01.labs.sftlyr.ws',
                'hostname': u'minion05',
                'datacenter': u'hkg02',
                'flavor': 'BL1_1X2X100'
                'dedicated': False,
                'private': False,
                'transient': False,
                'os_code' : u'UBUNTU_LATEST',
                'hourly': True,
                'ssh_keys': [1234],
                'disks': ('100','25'),
                'local_disk': True,
                'tags': 'test, pleaseCancel',
                'public_security_groups': [12, 15]
            }

            vsi = mgr.verify_create_instance(**new_vsi)
            # vsi will be a SoftLayer_Container_Product_Order_Virtual_Guest
            # if your order is correct. Otherwise you will get an exception
            print vsi
        """
        kwargs.pop('tags', None)
        create_options = self._generate_create_dict(**kwargs)
        template = self.guest.generateOrderTemplate(create_options)
        if kwargs.get('public_router') or kwargs.get('private_router'):
            if kwargs.get('private_vlan') or kwargs.get('public_vlan') or kwargs.get('private_subnet') \
                    or kwargs.get('public_subnet'):
                raise exceptions.SoftLayerError("You have to select network vlan or network vlan with a subnet or "
                                                "only router, not all options")
            vsi = template['virtualGuests'][0]
            network_components = self._create_network_components(kwargs.get('public_vlan', None),
                                                                 kwargs.get('private_vlan', None),
                                                                 kwargs.get('private_subnet', None),
                                                                 kwargs.get('public_subnet', None),
                                                                 kwargs.get('private_router', None),
                                                                 kwargs.get('public_router', None))
            vsi.update(network_components)

        if kwargs.get('private_subnet') or kwargs.get('public_subnet'):
            vsi = template['virtualGuests'][0]
            network_components = self._create_network_components(kwargs.get('public_vlan', None),
                                                                 kwargs.get('private_vlan', None),
                                                                 kwargs.get('private_subnet', None),
                                                                 kwargs.get('public_subnet', None))
            vsi.update(network_components)

        return template

    def create_instance(self, **kwargs):
        """Creates a new virtual server instance.

        .. warning::

            This will add charges to your account

        Example::

            new_vsi = {
                'domain': u'test01.labs.sftlyr.ws',
                'hostname': u'minion05',
                'datacenter': u'hkg02',
                'flavor': 'BL1_1X2X100'
                'dedicated': False,
                'private': False,
                'os_code' : u'UBUNTU_LATEST',
                'hourly': True,
                'ssh_keys': [1234],
                'disks': ('100','25'),
                'local_disk': True,
                'tags': 'test, pleaseCancel',
                'public_security_groups': [12, 15]
            }

            vsi = mgr.create_instance(**new_vsi)
            # vsi will have the newly created vsi details if done properly.
            print vsi

        :param int cpus: The number of virtual CPUs to include in the instance.
        :param int memory: The amount of RAM to order.
        :param bool hourly: Flag to indicate if this server should be billed hourly (default) or monthly.
        :param string hostname: The hostname to use for the new server.
        :param string domain: The domain to use for the new server.
        :param bool local_disk: Flag to indicate if this should be a local disk (default) or a SAN disk.
        :param string datacenter: The short name of the data center in which the VS should reside.
        :param string os_code: The operating system to use. Cannot be specified  if image_id is specified.
        :param int image_id: The GUID of the image to load onto the server. Cannot be specified if os_code is specified.
        :param bool dedicated: Flag to indicate if this should be housed on adedicated or shared host (default).
                               This will incur a fee on your account.
        :param int public_vlan: The ID of the public VLAN on which you want this VS placed.
        :param list public_security_groups: The list of security group IDs to apply to the public interface
        :param list private_security_groups: The list of security group IDs to apply to the private interface
        :param int private_vlan: The ID of the private VLAN on which you want  this VS placed.
        :param list disks: A list of disk capacities for this server.
        :param string post_uri: The URI of the post-install script to run  after reload
        :param bool private: If true, the VS will be provisioned only with access to the private network.
                             Defaults to false
        :param list ssh_keys: The SSH keys to add to the root user
        :param int nic_speed: The port speed to set
        :param string tags: tags to set on the VS as a comma separated list
        :param string flavor: The key name of the public virtual server flavor being ordered.
        :param int host_id: The host id of a dedicated host to provision a dedicated host virtual server on.
        """
        tags = kwargs.pop('tags', None)
        inst = self.guest.createObject(self._generate_create_dict(**kwargs))
        if tags is not None:
            self.set_tags(tags, guest_id=inst['id'])
        return inst

    @retry(logger=LOGGER)
    def set_tags(self, tags, guest_id):
        """Sets tags on a guest with a retry decorator

        Just calls guest.setTags, but if it fails from an APIError will retry
        """
        self.guest.setTags(tags, id=guest_id)

    def create_instances(self, config_list):
        """Creates multiple virtual server instances.

        This takes a list of dictionaries using the same arguments as
        create_instance().

        .. warning::

            This will add charges to your account

        Example::

            # Define the instance we want to create.
            new_vsi = {
                'domain': u'test01.labs.sftlyr.ws',
                'hostname': u'minion05',
                'datacenter': u'hkg02',
                'flavor': 'BL1_1X2X100'
                'dedicated': False,
                'private': False,
                'os_code' : u'UBUNTU_LATEST',
                'hourly': True,
                'ssh_keys': [1234],
                'disks': ('100','25'),
                'local_disk': True,
                'tags': 'test, pleaseCancel',
                'public_security_groups': [12, 15]
            }

            # using .copy() so we can make changes to individual nodes
            instances = [new_vsi.copy(), new_vsi.copy(), new_vsi.copy()]

            # give each its own hostname, not required.
            instances[0]['hostname'] = "multi-test01"
            instances[1]['hostname'] = "multi-test02"
            instances[2]['hostname'] = "multi-test03"

            vsi = mgr.create_instances(config_list=instances)
            #vsi will be a dictionary of all the new virtual servers
            print vsi
        """
        tags = [conf.pop('tags', None) for conf in config_list]

        resp = self.guest.createObjects([self._generate_create_dict(**kwargs)
                                         for kwargs in config_list])

        for instance, tag in zip(resp, tags):
            if tag is not None:
                self.set_tags(tag, guest_id=instance['id'])

        return resp

    def change_port_speed(self, instance_id, public, speed):
        """Allows you to change the port speed of a virtual server's NICs.

        Example::

            #change the Public interface to 10Mbps on instance 12345
            result = mgr.change_port_speed(instance_id=12345,
                                        public=True, speed=10)
            # result will be True or an Exception

        :param int instance_id: The ID of the VS
        :param bool public: Flag to indicate which interface to change.
                            True (default) means the public interface.
                            False indicates the private interface.
        :param int speed: The port speed to set.

        .. warning::
            A port speed of 0 will disable the interface.
        """
        if public:
            return self.client.call('Virtual_Guest', 'setPublicNetworkInterfaceSpeed',
                                    speed, id=instance_id)
        else:
            return self.client.call('Virtual_Guest', 'setPrivateNetworkInterfaceSpeed',
                                    speed, id=instance_id)

    def _get_ids_from_hostname(self, hostname):
        """List VS ids which match the given hostname."""
        results = self.list_instances(hostname=hostname, mask="id")
        return [result['id'] for result in results]

    def _get_ids_from_ip(self, ip_address):  # pylint: disable=inconsistent-return-statements
        """List VS ids which match the given ip address."""
        try:
            # Does it look like an ip address?
            socket.inet_aton(ip_address)
        except socket.error:
            return []

        # Find the VS via ip address. First try public ip, then private
        results = self.list_instances(public_ip=ip_address, mask="id")
        if results:
            return [result['id'] for result in results]

        results = self.list_instances(private_ip=ip_address, mask="id")
        if results:
            return [result['id'] for result in results]

    def edit(self, instance_id, userdata=None, hostname=None, domain=None,
             notes=None, tags=None):
        """Edit hostname, domain name, notes, and/or the user data of a VS.

        Parameters set to None will be ignored and not attempted to be updated.

        :param integer instance_id: the instance ID to edit
        :param string userdata: user data on VS to edit.
                                If none exist it will be created
        :param string hostname: valid hostname
        :param string domain: valid domain namem
        :param string notes: notes about this particular VS
        :param string tags: tags to set on the VS as a comma separated list.
                            Use the empty string to remove all tags.
        :returns: bool -- True or an Exception

        Example::
            # Change the hostname on instance 12345 to 'something'
            result = mgr.edit(instance_id=12345 , hostname="something")
            #result will be True or an Exception
        """

        obj = {}
        if userdata:
            self.guest.setUserMetadata([userdata], id=instance_id)

        if tags is not None:
            self.set_tags(tags, guest_id=instance_id)

        if hostname:
            obj['hostname'] = hostname

        if domain:
            obj['domain'] = domain

        if notes:
            obj['notes'] = notes

        if not obj:
            return True

        return self.guest.editObject(obj, id=instance_id)

    def rescue(self, instance_id):
        """Reboot a VSI into the Xen recsue kernel.

        :param integer instance_id: the instance ID to rescue
        :returns: bool -- True or an Exception

        Example::
            # Puts instance 12345 into rescue mode
            result = mgr.rescue(instance_id=12345)
        """
        return self.guest.executeRescueLayer(id=instance_id)

    def capture(self, instance_id, name, additional_disks=False, notes=None):
        """Capture one or all disks from a VS to a SoftLayer image.

        Parameters set to None will be ignored and not attempted to be updated.

        :param integer instance_id: the instance ID to edit
        :param string name: name assigned to the image
        :param bool additional_disks: set to true to include all additional
                                        attached storage devices
        :param string notes: notes about this particular image

        :returns: dictionary -- information about the capture transaction.

        Example::
            name = "Testing Images"
            notes = "Some notes about this image"
            result = mgr.capture(instance_id=12345, name=name, notes=notes)
        """

        vsi = self.client.call(
            'Virtual_Guest',
            'getObject',
            id=instance_id,
            mask="""id,
            blockDevices[id,device,mountType,
            diskImage[id,metadataFlag,type[keyName]]]""")

        disks_to_capture = []
        for block_device in vsi['blockDevices']:

            # We never want metadata disks
            if utils.lookup(block_device, 'diskImage', 'metadataFlag'):
                continue

            # We never want swap devices
            type_name = utils.lookup(block_device, 'diskImage', 'type', 'keyName')
            if type_name == 'SWAP':
                continue

            # We never want CD images
            if block_device['mountType'] == 'CD':
                continue

            # Only use the first block device if we don't want additional disks
            if not additional_disks and str(block_device['device']) != '0':
                continue

            disks_to_capture.append(block_device)

        return self.guest.createArchiveTransaction(
            name, disks_to_capture, notes, id=instance_id)

    def upgrade(self, instance_id, cpus=None, memory=None, nic_speed=None, public=True, preset=None, disk=None):
        """Upgrades a VS instance.

        Example::

           # Upgrade instance 12345 to 4 CPUs and 4 GB of memory
           import SoftLayer
           client = SoftLayer.create_client_from_env()
           mgr = SoftLayer.VSManager(client)
           mgr.upgrade(12345, cpus=4, memory=4)

        :param int instance_id: Instance id of the VS to be upgraded
        :param int cpus: The number of virtual CPUs to upgrade to
                            of a VS instance.
        :param string preset: preset assigned to the vsi
        :param int memory: RAM of the VS to be upgraded to.
        :param int nic_speed: The port speed to set
        :param bool public: CPU will be in Private/Public Node.

        :returns: bool
        """
        upgrade_prices = self._get_upgrade_prices(instance_id)
        prices = []

        data = {'nic_speed': nic_speed}

        if cpus is not None and preset is not None:
            raise ValueError("Do not use cpu, private and memory if you are using flavors")
        data['cpus'] = cpus

        if memory is not None and preset is not None:
            raise ValueError("Do not use memory, private or cpu if you are using flavors")
        data['memory'] = memory

        maintenance_window = datetime.datetime.now(utils.UTC())
        order = {
            'complexType': 'SoftLayer_Container_Product_Order_Virtual_Guest_Upgrade',
            'properties': [{
                'name': 'MAINTENANCE_WINDOW',
                'value': maintenance_window.strftime("%Y-%m-%d %H:%M:%S%z")
            }],
            'virtualGuests': [{'id': int(instance_id)}],
        }

        if disk:
            disk_number = 0
            vsi_disk = self.get_instance(instance_id)
            for item in vsi_disk.get('billingItem').get('children'):
                if item.get('categoryCode').__contains__('guest_disk'):
                    if disk_number < int("".join(filter(str.isdigit, item.get('categoryCode')))):
                        disk_number = int("".join(filter(str.isdigit, item.get('categoryCode'))))
            for disk_guest in disk:
                if disk_guest.get('number') > 0:
                    price_id = self._get_price_id_for_upgrade_option(upgrade_prices, 'disk',
                                                                     disk_guest.get('capacity'),
                                                                     public)
                    disk_number = disk_guest.get('number')

                else:
                    price_id = self._get_price_id_for_upgrade_option(upgrade_prices, 'disk',
                                                                     disk_guest.get('capacity'),
                                                                     public)
                    disk_number = disk_number + 1

                if price_id is None:
                    raise exceptions.SoftLayerAPIError(500,
                                                       'Unable to find %s option with value %s' % (
                                                           ('disk', disk_guest.get('capacity'))))

                category = {'categories': [{
                    'categoryCode': 'guest_disk' + str(disk_number),
                    'complexType': "SoftLayer_Product_Item_Category"}],
                            'complexType': 'SoftLayer_Product_Item_Price',
                            'id': price_id}

                prices.append(category)
            order['prices'] = prices

        for option, value in data.items():
            if not value:
                continue
            price_id = self._get_price_id_for_upgrade_option(upgrade_prices,
                                                             option,
                                                             value,
                                                             public)
            if not price_id:
                # Every option provided is expected to have a price
                raise exceptions.SoftLayerError(
                    "Unable to find %s option with value %s" % (option, value))

            prices.append({'id': price_id})

            order['prices'] = prices
        if preset is not None:
            vs_object = self.get_instance(instance_id)['billingItem']['package']
            order['presetId'] = self.ordering_manager.get_preset_by_key(vs_object['keyName'], preset)['id']

        if prices or preset:
            self.client['Product_Order'].placeOrder(order)
            return True
        return False

    def order_guest(self, guest_object, test=False):
        """Uses Product_Order::placeOrder to create a virtual guest.

        Useful when creating a virtual guest with options not supported by Virtual_Guest::createObject
        specifically ipv6 support.

        :param dictionary guest_object: See SoftLayer.CLI.virt.create._parse_create_args

        Example::

            new_vsi = {
                'domain': u'test01.labs.sftlyr.ws',
                'hostname': u'minion05',
                'datacenter': u'hkg02',
                'flavor': 'BL1_1X2X100'
                'dedicated': False,
                'private': False,
                'transient': False,
                'os_code' : u'UBUNTU_LATEST',
                'hourly': True,
                'ssh_keys': [1234],
                'disks': ('100','25'),
                'local_disk': True,
                'tags': 'test, pleaseCancel',
                'public_security_groups': [12, 15],
                'ipv6': True
            }

            vsi = mgr.order_guest(new_vsi)
            # vsi will have the newly created vsi receipt.
            # vsi['orderDetails']['virtualGuests'] will be an array of created Guests
            print vsi
        """
        tags = guest_object.pop('tags', None)
        template = self.verify_create_instance(**guest_object)

        if guest_object.get('ipv6'):
            ipv6_price = self.ordering_manager.get_price_id_list('PUBLIC_CLOUD_SERVER', ['1_IPV6_ADDRESS'])
            template['prices'].append({'id': ipv6_price[0]})

        # Notice this is `userdata` from the cli, but we send it in as `userData`
        if guest_object.get('userdata'):
            # SL_Virtual_Guest::generateOrderTemplate() doesn't respect userData, so we need to add it ourself
            template['virtualGuests'][0]['userData'] = [{"value": guest_object.get('userdata')}]
        if guest_object.get('host_id'):
            template['hostId'] = guest_object.get('host_id')
        if guest_object.get('placement_id'):
            template['virtualGuests'][0]['placementGroupId'] = guest_object.get('placement_id')

        if test:
            result = self.client.call('Product_Order', 'verifyOrder', template)
        else:
            result = self.client.call('Product_Order', 'placeOrder', template)
            if tags is not None:
                virtual_guests = utils.lookup(result, 'orderDetails', 'virtualGuests')
                for guest in virtual_guests:
                    self.set_tags(tags, guest_id=guest['id'])
        return result

    def _get_package_items(self):
        """Following Method gets all the item ids related to VS.

        Deprecated in favor of _get_upgrade_prices()
        """
        warnings.warn("use _get_upgrade_prices() instead",
                      DeprecationWarning)
        mask = [
            'description',
            'capacity',
            'units',
            'prices[id,locationGroupId,categories[name,id,categoryCode]]'
        ]
        mask = "mask[%s]" % ','.join(mask)

        package_keyname = "CLOUD_SERVER"
        package = self.ordering_manager.get_package_by_key(package_keyname)

        package_service = self.client['Product_Package']
        return package_service.getItems(id=package['id'], mask=mask)

    def _get_upgrade_prices(self, instance_id, include_downgrade_options=True):
        """Following Method gets all the price ids related to upgrading a VS.

        :param int instance_id: Instance id of the VS to be upgraded

        :returns: list
        """
        mask = [
            'id',
            'locationGroupId',
            'categories[name,id,categoryCode]',
            'item[description,capacity,units]'
        ]
        mask = "mask[%s]" % ','.join(mask)
        return self.guest.getUpgradeItemPrices(include_downgrade_options, id=instance_id, mask=mask)

    # pylint: disable=inconsistent-return-statements
    def _get_price_id_for_upgrade_option(self, upgrade_prices, option, value, public=True):
        """Find the price id for the option and value to upgrade. This

        :param list upgrade_prices: Contains all the prices related to a VS upgrade
        :param string option: Describes type of parameter to be upgraded
        :param int value: The value of the parameter to be upgraded
        :param bool public: CPU will be in Private/Public Node.
        """
        option_category = {
            'memory': 'ram',
            'cpus': 'guest_core',
            'nic_speed': 'port_speed',
            'disk': 'guest_disk'
        }
        category_code = option_category.get(option)

        for price in upgrade_prices:
            if price.get('categories') is None or price.get('item') is None:
                continue

            product = price.get('item')
            is_private = (product.get('units') == 'PRIVATE_CORE'
                          or product.get('units') == 'DEDICATED_CORE')

            for category in price.get('categories'):
                if option == 'disk':
                    if (category_code == (''.join([i for i in category.get('categoryCode') if not i.isdigit()]))
                            and str(product.get('capacity')) == str(value)):
                        return price.get('id')

                if not (category.get('categoryCode') == category_code
                        and str(product.get('capacity')) == str(value)):
                    continue

                if option == 'cpus':
                    # Public upgrade and public guest_core price
                    if public and not is_private:
                        return price.get('id')
                    # Private upgrade and private guest_core price
                    elif not public and is_private:
                        return price.get('id')
                elif option == 'nic_speed':
                    if 'Public' in product.get('description'):
                        return price.get('id')
                else:
                    return price.get('id')

    def get_summary_data_usage(self, instance_id, start_date=None, end_date=None, valid_type=None, summary_period=None):
        """Retrieve the usage information of a virtual server.

        :param string instance_id: a string identifier used to resolve ids
        :param string start_date: the start data to retrieve the vs usage information
        :param string end_date: the start data to retrieve the vs usage information
        :param string string valid_type: the Metric_Data_Type keyName.
        :param int summary_period: summary period.
        """
        valid_types = [
            {
                "keyName": valid_type,
                "summaryType": "max"
            }
        ]

        metric_tracking_id = self.get_tracking_id(instance_id)

        return self.client.call('Metric_Tracking_Object', 'getSummaryData', start_date, end_date, valid_types,
                                summary_period, id=metric_tracking_id, iter=True)

    def get_tracking_id(self, instance_id):
        """Returns the Metric Tracking Object Id for a hardware server

        :param int instance_id: Id of the hardware server
        """
        return self.guest.getMetricTrackingObjectId(id=instance_id)

    def get_bandwidth_data(self, instance_id, start_date=None, end_date=None, direction=None, rollup=3600):
        """Gets bandwidth data for a server

        Will get averaged bandwidth data for a given time period. If you use a rollup over 3600 be aware
        that the API will bump your start/end date to align with how data is stored. For example if you
        have a rollup of 86400 your start_date will be bumped to 00:00. If you are not using a time in the
        start/end date fields, this won't really matter.

        :param int instance_id: Hardware Id to get data for
        :param date start_date: Date to start pulling data for.
        :param date end_date: Date to finish pulling data for
        :param string direction: Can be either 'public', 'private', or None for both.
        :param int rollup: 300, 600, 1800, 3600, 43200 or 86400 seconds to average data over.
        """
        tracking_id = self.get_tracking_id(instance_id)
        data = self.client.call('Metric_Tracking_Object', 'getBandwidthData', start_date, end_date, direction,
                                rollup, id=tracking_id, iter=True)
        return data

    def get_bandwidth_allocation(self, instance_id):
        """Combines getBandwidthAllotmentDetail() and getBillingCycleBandwidthUsage() """
        a_mask = "mask[allocation[amount]]"
        allotment = self.client.call('Virtual_Guest', 'getBandwidthAllotmentDetail', id=instance_id, mask=a_mask)
        u_mask = "mask[amountIn,amountOut,type]"
        usage = self.client.call('Virtual_Guest', 'getBillingCycleBandwidthUsage', id=instance_id, mask=u_mask)
        if allotment:
            return {'allotment': allotment.get('allocation'), 'usage': usage}
        return {'allotment': allotment, 'usage': usage}

    # pylint: disable=inconsistent-return-statements
    def _get_price_id_for_upgrade(self, package_items, option, value, public=True):
        """Find the price id for the option and value to upgrade.

        Deprecated in favor of _get_price_id_for_upgrade_option()

        :param list package_items: Contains all the items related to an VS
        :param string option: Describes type of parameter to be upgraded
        :param int value: The value of the parameter to be upgraded
        :param bool public: CPU will be in Private/Public Node.
        """
        warnings.warn("use _get_price_id_for_upgrade_option() instead",
                      DeprecationWarning)
        option_category = {
            'memory': 'ram',
            'cpus': 'guest_core',
            'nic_speed': 'port_speed'
        }
        category_code = option_category[option]
        for item in package_items:
            is_private = (item.get('units') == 'PRIVATE_CORE')
            for price in item['prices']:
                if 'locationGroupId' in price and price['locationGroupId']:
                    # Skip location based prices
                    continue

                if 'categories' not in price:
                    continue

                categories = price['categories']
                for category in categories:
                    if not (category['categoryCode'] == category_code
                            and str(item['capacity']) == str(value)):
                        continue
                    if option == 'cpus':
                        if public and not is_private:
                            return price['id']
                        elif not public and is_private:
                            return price['id']
                    elif option == 'nic_speed':
                        if 'Public' in item['description']:
                            return price['id']
                    else:
                        return price['id']

    def get_storage_details(self, instance_id, nas_type):
        """Returns the virtual server attached network storage.

        :param int instance_id: Id of the virtual server
        :param nas_type: storage type.
        """
        mask = 'mask[id,username,capacityGb,notes,serviceResourceBackendIpAddress,' \
               'allowedVirtualGuests[id,datacenter]]'
        return self.guest.getAttachedNetworkStorages(nas_type, mask=mask, id=instance_id)

    def get_storage_credentials(self, instance_id):
        """Returns the virtual server storage credentials.

        :param int instance_id: Id of the virtual server
        """
        mask = 'mask[credential]'
        return self.guest.getAllowedHost(mask=mask, id=instance_id)

    def get_portable_storage(self, instance_id):
        """Returns the virtual server portable storage.

        :param int instance_id: Id of the virtual server
        """
        object_filter = {"portableStorageVolumes": {"blockDevices": {"guest": {"id": {"operation": instance_id}}}}}
        return self.account.getPortableStorageVolumes(filter=object_filter)

    def get_local_disks(self, instance_id):
        """Returns the virtual server local disks.

        :param int instance_id: Id of the virtual server
        """
        mask = 'mask[diskImage]'
        return self.guest.getBlockDevices(mask=mask, id=instance_id)

    def migrate(self, instance_id):
        """Calls SoftLayer_Virtual_Guest::migrate

        Only actually does anything if the virtual server requires a migration.
        Will return an exception otherwise.

        :param int instance_id: Id of the virtual server
        """
        return self.guest.migrate(id=instance_id)

    def migrate_dedicated(self, instance_id, host_id):
        """Calls SoftLayer_Virtual_Guest::migrate

        Only actually does anything if the virtual server requires a migration.
        Will return an exception otherwise.

        :param int instance_id: Id of the virtual server
        """
        return self.guest.migrateDedicatedHost(host_id, id=instance_id)

    def get_hardware_guests(self):
        """Returns all virtualHost capable hardware objects and their guests.

        :return SoftLayer_Hardware[].
        """
        object_filter = {"hardware": {"virtualHost": {"id": {"operation": "not null"}}}}
        mask = "mask[virtualHost[guests[powerState]]]"
        return self.client.call('SoftLayer_Account', 'getHardware', mask=mask, filter=object_filter)

    def authorize_storage(self, vs_id, username_storage):
        """Authorize File or Block Storage to a Virtual Server.

        :param int vs_id: Virtual server id.
        :param string username_storage: Storage username.

        :return: bool.
        """
        _filter = {"networkStorage": {"username": {"operation": username_storage}}}

        storage_result = self.client.call('Account', 'getNetworkStorage', filter=_filter)

        if len(storage_result) == 0:
            raise SoftLayerError("The Storage with username: %s was not found, please"
                                 " enter a valid storage username" % username_storage)

        storage_template = [
            {
                "id": storage_result[0]['id'],
                "username": username_storage
            }
        ]

        result = self.client.call('SoftLayer_Virtual_Guest', 'allowAccessToNetworkStorageList',
                                  storage_template, id=vs_id)

        return result

    def attach_portable_storage(self, vs_id, portable_id):
        """Attach portal storage to a Virtual Server.

        :param int vs_id: Virtual server id.
        :param int portable_id: Portal storage id.

        :return: SoftLayer_Provisioning_Version1_Transaction.
        """
        disk_id = portable_id
        result = self.client.call('SoftLayer_Virtual_Guest', 'attachDiskImage',
                                  disk_id, id=vs_id)

        return result
