"""
    SoftLayer.vs
    ~~~~~~~~~~~~
    VS Manager/helpers

    :license: MIT, see LICENSE for more details.
"""
import socket
from time import sleep
import datetime
from itertools import repeat

from SoftLayer.utils import NestedDict, query_filter, IdentifierMixin, lookup


class VSManager(IdentifierMixin, object):
    """ Manage Virtual Servers """
    def __init__(self, client):
        self.client = client
        self.account = client['Account']
        self.guest = client['Virtual_Guest']
        self.resolvers = [self._get_ids_from_ip, self._get_ids_from_hostname]

    def list_instances(self, hourly=True, monthly=True, tags=None, cpus=None,
                       memory=None, hostname=None, domain=None,
                       local_disk=None, datacenter=None, nic_speed=None,
                       public_ip=None, private_ip=None, **kwargs):
        """ Retrieve a list of all virtual servers on the account.

        :param boolean hourly: include hourly instances
        :param boolean monthly: include monthly instances
        :param list tags: filter based on tags
        :param integer cpus: filter based on number of CPUS
        :param integer memory: filter based on amount of memory
        :param string hostname: filter based on hostname
        :param string domain: filter based on domain
        :param string local_disk: filter based on local_disk
        :param string datacenter: filter based on datacenter
        :param integer nic_speed: filter based on network speed (in MBPS)
        :param string public_ip: filter based on public ip address
        :param string private_ip: filter based on private ip address
        :param dict \\*\\*kwargs: response-level options (mask, limit, etc.)
        :returns: Returns a list of dictionaries representing the matching
                  virtual servers

        ::

           # Print out a list of all hourly instances in the DAL05 data center.
           # env variables
           # SL_USERNAME = YOUR_USERNAME
           # SL_API_KEY = YOUR_API_KEY
           import SoftLayer
           client = SoftLayer.Client()

           mgr = SoftLayer.VSManager(client)
           for vsi in mgr.list_instances(hourly=True, datacenter='dal05'):
               print vsi['fullyQualifiedDomainName'], vs['primaryIpAddress']

        """
        if 'mask' not in kwargs:
            items = set([
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
            ])
            kwargs['mask'] = "mask[%s]" % ','.join(items)

        call = 'getVirtualGuests'
        if not all([hourly, monthly]):
            if hourly:
                call = 'getHourlyVirtualGuests'
            elif monthly:
                call = 'getMonthlyVirtualGuests'

        _filter = NestedDict(kwargs.get('filter') or {})
        if tags:
            _filter['virtualGuests']['tagReferences']['tag']['name'] = {
                'operation': 'in',
                'options': [{'name': 'data', 'value': tags}],
            }

        if cpus:
            _filter['virtualGuests']['maxCpu'] = query_filter(cpus)

        if memory:
            _filter['virtualGuests']['maxMemory'] = query_filter(memory)

        if hostname:
            _filter['virtualGuests']['hostname'] = query_filter(hostname)

        if domain:
            _filter['virtualGuests']['domain'] = query_filter(domain)

        if local_disk is not None:
            _filter['virtualGuests']['localDiskFlag'] = \
                query_filter(bool(local_disk))

        if datacenter:
            _filter['virtualGuests']['datacenter']['name'] = \
                query_filter(datacenter)

        if nic_speed:
            _filter['virtualGuests']['networkComponents']['maxSpeed'] = \
                query_filter(nic_speed)

        if public_ip:
            _filter['virtualGuests']['primaryIpAddress'] = \
                query_filter(public_ip)

        if private_ip:
            _filter['virtualGuests']['primaryBackendIpAddress'] = \
                query_filter(private_ip)

        kwargs['filter'] = _filter.to_dict()
        func = getattr(self.account, call)
        return func(**kwargs)

    def get_instance(self, instance_id, **kwargs):
        """ Get details about a virtual server instance

        :param integer instance_id: the instance ID
        :returns: A dictionary containing a large amount of information about
                  the specified instance.

        """

        if 'mask' not in kwargs:
            items = set([
                'id',
                'globalIdentifier',
                'fullyQualifiedDomainName',
                'hostname',
                'domain',
                'createDate',
                'modifyDate',
                'provisionDate',
                'notes',
                'dedicatedAccountHostOnlyFlag',
                'privateNetworkOnlyFlag',
                'primaryBackendIpAddress',
                'primaryIpAddress',
                'networkComponents[id, status, speed, maxSpeed, name,'
                'macAddress, primaryIpAddress, port, primarySubnet]',
                'lastKnownPowerState.name',
                'powerState',
                'status',
                'maxCpu',
                'maxMemory',
                'datacenter',
                'activeTransaction[id, transactionStatus[friendlyName,name]]',
                'lastOperatingSystemReload.id',
                'blockDevices',
                'blockDeviceTemplateGroup[id, name, globalIdentifier]',
                'postInstallScriptUri',
                'userData',
                'operatingSystem.softwareLicense.'
                'softwareDescription[manufacturer,name,version,referenceCode]',
                'operatingSystem.passwords[username,password]',
                'hourlyBillingFlag',
                'billingItem.recurringFee',
                'tagReferences[id,tag[name,id]]',
                'networkVlans[id,vlanNumber,networkSpace]',
            ])
            kwargs['mask'] = "mask[%s]" % ','.join(items)

        return self.guest.getObject(id=instance_id, **kwargs)

    def get_create_options(self):
        """ Retrieves the available options for creating a VS.

        :returns: A dictionary of creation options.

        """
        return self.guest.getCreateObjectOptions()

    def cancel_instance(self, instance_id):
        """ Cancel an instance immediately, deleting all its data.

        :param integer instance_id: the instance ID to cancel

        """
        return self.guest.deleteObject(id=instance_id)

    def reload_instance(self, instance_id, post_uri=None, ssh_keys=None):
        """ Perform an OS reload of an instance with its current configuration.

        :param integer instance_id: the instance ID to reload
        :param string post_url: The URI of the post-install script to run
                                after reload
        :param list ssh_keys: The SSH keys to add to the root user
        """
        config = {}

        if post_uri:
            config['customProvisionScriptUri'] = post_uri

        if ssh_keys:
            config['sshKeyIds'] = [key_id for key_id in ssh_keys]

        return self.guest.reloadOperatingSystem('FORCE', config,
                                                id=instance_id)

    def _generate_create_dict(
            self, cpus=None, memory=None, hourly=True,
            hostname=None, domain=None, local_disk=True,
            datacenter=None, os_code=None, image_id=None,
            dedicated=False, public_vlan=None, private_vlan=None,
            userdata=None, nic_speed=None, disks=None, post_uri=None,
            private=False, ssh_keys=None):
        """ Returns a dict appropriate to pass into Virtual_Guest::createObject
            See :func:`create_instance` for a list of available options.
        """
        required = [cpus, memory, hostname, domain]

        mutually_exclusive = [
            {'os_code': os_code, "image_id": image_id},
        ]

        if not all(required):
            raise ValueError("cpu, memory, hostname, and domain are required")

        for mu_ex in mutually_exclusive:
            if all(mu_ex.values()):
                raise ValueError(
                    'Can only specify one of: %s' % (','.join(mu_ex.keys())))

        data = {
            "startCpus": int(cpus),
            "maxMemory": int(memory),
            "hostname": hostname,
            "domain": domain,
            "localDiskFlag": local_disk,
        }

        data["hourlyBillingFlag"] = hourly

        if dedicated:
            data["dedicatedAccountHostOnlyFlag"] = dedicated

        if private:
            data['privateNetworkOnlyFlag'] = private

        if image_id:
            data["blockDeviceTemplateGroup"] = {"globalIdentifier": image_id}
        elif os_code:
            data["operatingSystemReferenceCode"] = os_code

        if datacenter:
            data["datacenter"] = {"name": datacenter}

        if public_vlan:
            data.update({
                'primaryNetworkComponent': {
                    "networkVlan": {"id": int(public_vlan)}}})
        if private_vlan:
            data.update({
                "primaryBackendNetworkComponent": {
                    "networkVlan": {"id": int(private_vlan)}}})

        if userdata:
            data['userData'] = [{'value': userdata}]

        if nic_speed:
            data['networkComponents'] = [{'maxSpeed': nic_speed}]

        if disks and isinstance(disks, list):
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

    def wait_for_transaction(self, instance_id, limit, delay=1):
        """ Waits on a VS transaction for the specified amount of time.
        is really just a wrapper for wait_for_ready(pending=True).
        Provided for backwards compatibility.


        :param int instance_id: The instance ID with the pending transaction
        :param int limit: The maximum amount of time to wait.
        :param int delay: The number of seconds to sleep before checks.
                          Defaults to 1.
        """

        return self.wait_for_ready(instance_id, limit, delay=delay,
                                   pending=True)

    def wait_for_ready(self, instance_id, limit, delay=1, pending=False):
        """ Determine if a VS is ready and available.  In some cases
        though, that can mean that no transactions are running. The default
        arguments imply a VS is operational and ready for use by having
        network connectivity and remote access is available.  Setting
        ``pending=True`` will ensure future API calls
        against this instance will not error due to pending
        transactions such as OS Reloads and cancellations.

        :param int instance_id: The instance ID with the pending transaction
        :param int limit: The maximum amount of time to wait.
        :param int delay: The number of seconds to sleep before checks.
                          Defaults to 1.
        :param bool pending: Wait for pending transactions not related to
                             provisioning or reloads such as monitoring.
        """
        for count, new_instance in enumerate(repeat(instance_id), start=1):
            instance = self.get_instance(new_instance)
            last_reload = lookup(instance, 'lastOperatingSystemReload', 'id')
            active_transaction = lookup(instance, 'activeTransaction', 'id')

            reloading = all((
                active_transaction,
                last_reload,
                last_reload == active_transaction
            ))

            # only check for outstanding transactions if requested
            outstanding = False
            if pending:
                outstanding = active_transaction

            # return True if the instance has only if the instance has
            # finished provisioning and isn't currently reloading the OS.
            if instance.get('provisionDate') \
                    and not reloading and not outstanding:
                return True

            if count >= limit:
                return False

            sleep(delay)

    def verify_create_instance(self, **kwargs):
        """ Verifies an instance creation command without actually placing an
        order. See :func:`create_instance` for a list of available
        options. """
        create_options = self._generate_create_dict(**kwargs)
        return self.guest.generateOrderTemplate(create_options)

    def create_instance(self, **kwargs):
        """
        Creates a new virtual server instance

        :param int cpus: The number of virtual CPUs to include in the instance.
        :param int memory: The amount of RAM to order.
        :param bool hourly: Flag to indicate if this server should be billed
                            hourly (default) or monthly.
        :param string hostname: The hostname to use for the new server.
        :param string domain: The domain to use for the new server.
        :param bool local_disk: Flag to indicate if this should be a local disk
                                (default) or a SAN disk.
        :param string datacenter: The short name of the data center in which
                                  the VS should reside.
        :param string os_code: The operating system to use. Cannot be specified
                               if image_id is specified.
        :param int image_id: The ID of the image to load onto the server.
                             Cannot be specified if os_code is specified.
        :param bool dedicated: Flag to indicate if this should be housed on a
                               dedicated or shared host (default). This will
                               incur a fee on your account.
        :param int public_vlan: The ID of the public VLAN on which you want
                                this VS placed.
        :param int private_vlan: The ID of the public VLAN on which you want
                                 this VS placed.
        :param bool bare_metal: Flag to indicate if this is a bare metal server
                                or a dedicated server (default).
        :param list disks: A list of disk capacities for this server.
        :param string post_uri: The URI of the post-install script to run
                                after reload
        :param bool private: If true, the VS will be provisioned only with
                             access to the private network. Defaults to false
        :param list ssh_keys: The SSH keys to add to the root user
        """
        create_options = self._generate_create_dict(**kwargs)
        return self.guest.createObject(create_options)

    def change_port_speed(self, instance_id, public, speed):
        """ Allows you to change the port speed of a virtual server's NICs.

        :param int instance_id: The ID of the VS
        :param bool public: Flag to indicate which interface to change.
                            True (default) means the public interface.
                            False indicates the private interface.
        :param int speed: The port speed to set.
        """
        if public:
            func = self.guest.setPublicNetworkInterfaceSpeed
        else:
            func = self.guest.setPrivateNetworkInterfaceSpeed

        return func(speed, id=instance_id)

    def _get_ids_from_hostname(self, hostname):
        """ List VS ids which match the given hostname """
        results = self.list_instances(hostname=hostname, mask="id")
        return [result['id'] for result in results]

    def _get_ids_from_ip(self, ip_address):
        """ List VS ids which match the given ip address """
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
             notes=None):
        """ Edit hostname, domain name, notes, and/or the user data of a VS

        Parameters set to None will be ignored and not attempted to be updated.

        :param integer instance_id: the instance ID to edit
        :param string userdata: user data on VS to edit.
                                If none exist it will be created
        :param string hostname: valid hostname
        :param string domain: valid domain namem
        :param string notes: notes about this particular VS

        """

        obj = {}
        if userdata:
            self.guest.setUserMetadata([userdata], id=instance_id)

        if hostname:
            obj['hostname'] = hostname

        if domain:
            obj['domain'] = domain

        if notes:
            obj['notes'] = notes

        if not obj:
            return True

        return self.guest.editObject(obj, id=instance_id)

    def capture(self, instance_id, name, additional_disks=False, notes=None):
        """ Capture one or all disks from a VS to a SoftLayer image.

        Parameters set to None will be ignored and not attempted to be updated.

        :param integer instance_id: the instance ID to edit
        :param string name: name assigned to the image
        :param string additional_disks: set to true to include all additional
                                        attached storage devices
        :param string notes: notes about this particular image

        """
        vsi = self.get_instance(instance_id)

        disk_filter = lambda x: x['device'] == '0'
        # Disk 1 is swap partition.  Need to skip its capture.
        if additional_disks:
            disk_filter = lambda x: x['device'] != '1'

        disks = [block_device for block_device in vsi['blockDevices']
                 if disk_filter(block_device)]

        return self.guest.createArchiveTransaction(
            name, disks, notes, id=instance_id)

    def upgrade(self, instance_id, cpus=None, memory=None,
                nic_speed=None, public=True):
        """
        Upgrades a VS instance
        :param int instance_id: Instance id of the VS to be upgraded
        :param int cpus: The number of virtual CPUs to upgrade to
                            of a VS instance.
        :param bool public: CPU will be in Private/Public Node.
        :param int memory: RAM of the VS to be upgraded to.
        :param int nic_speed: The port speed to set
        """
        package_items = self._get_package_items()
        item_id = []
        if cpus:
            item_id.append({'id': self._get_item_id_for_upgrade(
                            package_items, 'cpus', cpus, public)})
        if memory:
            item_id.append({'id': self._get_item_id_for_upgrade(
                            package_items, 'memory', memory)})
        if nic_speed:
            item_id.append({'id': self._get_item_id_for_upgrade(
                            package_items, 'nic_speed',
                            nic_speed)})
        order = {}
        order['complexType'] = \
            'SoftLayer_Container_Product_Order_Virtual_Guest_Upgrade'
        order['virtualGuests'] = [{'id': int(instance_id)}]
        order['prices'] = item_id
        order['properties'] = [{'name': 'MAINTENANCE_WINDOW',
                                        'value': str(datetime.datetime.now())}]
        if cpus or memory or nic_speed:
            self.client['Product_Order'].verifyOrder(order)
            self.client['Product_Order'].placeOrder(order)
            return True
        return False

    def _get_package_items(self):
        """
        Following Method gets all the item ids related to VS
        """
        mask = "mask[description,capacity,prices.id,categories[name,id]]"
        package = self.client['Product_Package']
        return package.getItems(id=46, mask=mask)

    def _get_item_id_for_upgrade(self, package_items, option, value,
                                 public=True):
        """
        Find the item ids for the parameters you want to upgrade to.
        :param list package_items: Contains all the items related to an VS
        :param string option: Describes type of parameter to be upgraded
        :param int value: The value of the parameter to be upgraded
        :param bool public: CPU will be in Private/Public Node.
        """
        vs_id = {'memory': 3, 'cpus': 80, 'nic_speed': 26}
        for item in package_items:
            for j in range(len(item['categories'])):
                if not (item['categories'][j]['id'] == vs_id[option] and
                        item['capacity'] == str(value)):
                    continue
                if option == 'cpus':
                    if public and ('Private' not in item['description']):
                        return item['prices'][0]['id']
                    elif not public and ('Private' in item['description']):
                        return item['prices'][0]['id']
                elif option == 'nic_speed':
                    if 'Public' in item['description']:
                        return item['prices'][0]['id']
                else:
                    return item['prices'][0]['id']
