"""
    SoftLayer.cci
    ~~~~~~~~~~~~~
    CCI Manager/helpers

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: MIT, see LICENSE for more details.
"""
import socket
from time import sleep
from itertools import repeat

from SoftLayer.utils import NestedDict, query_filter, IdentifierMixin


class CCIManager(IdentifierMixin, object):
    """ Manage CCIs """
    def __init__(self, client):
        #: A valid `SoftLayer.API.Client` object that will be used for all
        #: actions.
        self.client = client
        #: Reference to the SoftLayer_Account API object.
        self.account = client['Account']
        #: Reference to the SoftLayer_Virtual_Guest API object.
        self.guest = client['Virtual_Guest']
        #: A list of resolver functions. Used primarily by the CLI to provide
        #: a variety of methods for uniquely identifying an object such as
        #: hostname and IP address.
        self.resolvers = [self._get_ids_from_ip, self._get_ids_from_hostname]

    def list_instances(self, hourly=True, monthly=True, tags=None, cpus=None,
                       memory=None, hostname=None, domain=None,
                       local_disk=None, datacenter=None, nic_speed=None,
                       public_ip=None, private_ip=None, **kwargs):
        """ Retrieve a list of all CCIs on the account.

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
        :param dict \*\*kwargs: response-level arguments (limit, offset, etc.)
        :returns: Returns a list of dictionaries representing the matching CCIs

        ::

           # Print out a list of all hourly CCIs in the DAL05 data center.
           # env variables
           # SL_USERNAME = YOUR_USERNAME
           # SL_API_KEY = YOUR_API_KEY
           import SoftLayer
           client = SoftLayer.Client()

           mgr = SoftLayer.CCIManager(client)
           for cci in mgr.list_instances(hourly=True, datacenter='dal05'):
               print cci['fullyQualifiedDomainName'], cci['primaryIpAddress']

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
        """ Get details about a CCI instance

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
        """ Retrieves the available options for creating a CCI.

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
        payload = {
            'token': 'FORCE',
            'config': {},
        }

        if post_uri:
            payload['config']['customProvisionScriptUri'] = post_uri

        if ssh_keys:
            payload['config']['sshKeyIds'] = [key_id for key_id in ssh_keys]

        return self.guest.reloadOperatingSystem('FORCE', payload['config'],
                                                id=instance_id)

    def _generate_create_dict(
            self, cpus=None, memory=None, hourly=True,
            hostname=None, domain=None, local_disk=True,
            datacenter=None, os_code=None, image_id=None,
            dedicated=False, public_vlan=None, private_vlan=None,
            userdata=None, nic_speed=None, disks=None, post_uri=None,
            private=False, ssh_keys=None):
        """
        Translates a list of arguments into a dictionary necessary for creating
        a CCI.

        :param int cpus: The number of virtual CPUs to include in the instance.
        :param int memory: The amount of RAM to order.
        :param bool hourly: Flag to indicate if this server should be billed
                            hourly (default) or monthly.
        :param string hostname: The hostname to use for the new server.
        :param string domain: The domain to use for the new server.
        :param bool local_disk: Flag to indicate if this should be a local disk
                                (default) or a SAN disk.
        :param string datacenter: The short name of the data center in which
                                  the CCI should reside.
        :param string os_code: The operating system to use. Cannot be specified
                               if image_id is specified.
        :param int image_id: The ID of the image to load onto the server.
                             Cannot be specified if os_code is specified.
        :param bool dedicated: Flag to indicate if this should be housed on a
                               dedicated or shared host (default). This will
                               incur a fee on your account.
        :param int public_vlan: The ID of the public VLAN on which you want
                                this CCI placed.
        :param int private_vlan: The ID of the public VLAN on which you want
                                 this CCI placed.
        :param bool bare_metal: Flag to indicate if this is a bare metal server
                                or a dedicated server (default).
        :param list disks: A list of disk capacities for this server.
        :param string post_url: The URI of the post-install script to run
                                after reload
        :param bool private: If true, the CCI will be provisioned only with
                             access to the private network. Defaults to false
        :param list ssh_keys: The SSH keys to add to the root user
        """

        required = [cpus, memory, hostname, domain]

        mutually_exclusive = [
            {'os_code': os_code, "image_id": image_id},
        ]

        if not all(required):
            raise ValueError("cpu, memory, hostname, and domain are required")

        for me in mutually_exclusive:
            if all(me.values()):
                raise ValueError(
                    'Can only specify one of: %s' % (','.join(me.keys())))

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

            # disk 1 is reservered for swap
            # XXX: enumerate(iterator, start=0) was added in 2.6. work around
            # for 2.5 by adding 2 to the enumerated value
            for dev_id, disk in enumerate(disks[1:]):
                data['blockDevices'].append(
                    {
                        "device": str(dev_id + 2),
                        "diskImage": {"capacity": disk}
                    }
                )

        if post_uri:
            data['postInstallScriptUri'] = post_uri

        if ssh_keys:
            data['sshKeys'] = [{'id': key_id} for key_id in ssh_keys]

        return data

    def wait_for_transaction(self, instance_id, limit, delay=1):
        """ Waits on a CCI transaction for the specified amount of time.

        :param int instance_id: The instance ID with the pending transaction
        :param int limit: The maximum amount of time to wait.
        :param int delay: The number of seconds to sleep before checks.
                          Defaults to 1.
        """
        for count, new_instance in enumerate(repeat(instance_id)):
            instance = self.get_instance(new_instance)
            if not instance.get('activeTransaction', {}).get('id') and \
                    instance.get('provisionDate'):
                return True

            if count >= limit:
                return False

            sleep(delay)

    def verify_create_instance(self, **kwargs):
        """ Verifies an instance creation command without actually placing an
        order. See :func:`_generate_create_dict` for a list of available
        options. """
        create_options = self._generate_create_dict(**kwargs)
        return self.guest.generateOrderTemplate(create_options)

    def create_instance(self, **kwargs):
        """ Orders a new instance. See :func:`_generate_create_dict` for
        a list of available options. """
        create_options = self._generate_create_dict(**kwargs)
        return self.guest.createObject(create_options)

    def change_port_speed(self, instance_id, public, speed):
        """ Allows you to change the port speed of a CCI's NICs.

        :param int instance_id: The ID of the CCI
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
        results = self.list_instances(hostname=hostname, mask="id")
        return [result['id'] for result in results]

    def _get_ids_from_ip(self, ip):
        try:
            # Does it look like an ip address?
            socket.inet_aton(ip)
        except socket.error:
            return []

        # Find the CCI via ip address. First try public ip, then private
        results = self.list_instances(public_ip=ip, mask="id")
        if results:
            return [result['id'] for result in results]

        results = self.list_instances(private_ip=ip, mask="id")
        if results:
            return [result['id'] for result in results]

    def edit(self, instance_id, userdata=None, hostname=None, domain=None,
             notes=None):
        """ Edit hostname, domain name, notes, and/or the user data of a CCI

        Parameters set to None will be ignored and not attempted to be updated.

        :param integer instance_id: the instance ID to edit
        :param string userdata: user data on CCI to edit.
                                If none exist it will be created
        :param string hostname: valid hostname
        :param string domain: valid domain namem
        :param string notes: notes about this particular CCI

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
