"""
usage: sl cci [<command>] [<args>...] [options]

Manage, delete, order compute instances

The available commands are:
  network         Manage network settings
  edit            Edit details of a CCI
  create          Order and create a CCI
                    (see `sl cci create-options` for choices)
  manage          Manage active CCI
  list            List CCI's on the account
  detail          Output details about a CCI
  dns             DNS related actions to a CCI
  cancel          Cancel a running CCI
  create-options  Output available available options when creating a CCI
  reload          Reload the OS on a CCI based on its current configuration
  ready           Check if a CCI has finished provisioning

For several commands, <identifier> will be asked for. This can be the id,
hostname or the ip address for a CCI.
"""
# :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
# :license: BSD, see LICENSE for more details.

from os import linesep
import os.path

from SoftLayer import CCIManager, SshKeyManager
from SoftLayer.CLI import (
    CLIRunnable, Table, no_going_back, confirm, mb_to_gb, listing,
    FormattedItem)
from SoftLayer.CLI.helpers import (
    CLIAbort, ArgumentError, SequentialOutput, NestedDict, blank, resolve_id,
    KeyValueTable)


class ListCCIs(CLIRunnable):
    """
usage: sl cci list [--hourly | --monthly] [--sortby=SORT_COLUMN] [--tags=TAGS]
                   [options]

List CCIs

Examples:
    sl cci list --datacenter=dal05
    sl cci list --network=100 --cpu=2
    sl cci list --memory='>= 2048'
    sl cci list --tags=production,db

Options:
  --sortby=ARG  Column to sort by. options: id, datacenter, host,
                Cores, memory, primary_ip, backend_ip

Filters:
  --hourly                 Show hourly instances
  --monthly                Show monthly instances
  -H --hostname=HOST       Host portion of the FQDN. example: server
  -D --domain=DOMAIN       Domain portion of the FQDN. example: example.com
  -c --cpu=CPU             Number of CPU cores
  -m --memory=MEMORY       Memory in mebibytes (n * 1024)
  -d DC, --datacenter=DC   datacenter shortname (sng01, dal05, ...)
  -n MBPS, --network=MBPS  Network port speed in Mbps
  --tags=ARG               Only show instances that have one of these tags.
                           Comma-separated. (production,db)

For more on filters see 'sl help filters'
"""
    action = 'list'

    @staticmethod
    def execute(client, args):
        cci = CCIManager(client)

        tags = None
        if args.get('--tags'):
            tags = [tag.strip() for tag in args.get('--tags').split(',')]

        guests = cci.list_instances(
            hourly=args.get('--hourly'),
            monthly=args.get('--monthly'),
            hostname=args.get('--hostname'),
            domain=args.get('--domain'),
            cpus=args.get('--cpu'),
            memory=args.get('--memory'),
            datacenter=args.get('--datacenter'),
            nic_speed=args.get('--network'),
            tags=tags)

        t = Table([
            'id', 'datacenter', 'host',
            'cores', 'memory', 'primary_ip',
            'backend_ip', 'active_transaction',
        ])
        t.sortby = args.get('--sortby') or 'host'

        for guest in guests:
            guest = NestedDict(guest)
            t.add_row([
                guest['id'],
                guest['datacenter']['name'],
                guest['fullyQualifiedDomainName'],
                guest['maxCpu'],
                mb_to_gb(guest['maxMemory']),
                guest['primaryIpAddress'] or blank(),
                guest['primaryBackendIpAddress'] or blank(),
                guest['activeTransaction']['transactionStatus'].get(
                    'friendlyName') or blank(),
            ])

        return t


class CCIDetails(CLIRunnable):
    """
usage: sl cci detail [--passwords] [--price] <identifier> [options]

Get details for a CCI

Options:
  --passwords  Show passwords (check over your shoulder!)
  --price      Show associated prices
"""
    action = 'detail'

    @staticmethod
    def execute(client, args):
        cci = CCIManager(client)
        t = KeyValueTable(['Name', 'Value'])
        t.align['Name'] = 'r'
        t.align['Value'] = 'l'

        cci_id = resolve_id(cci.resolve_ids, args.get('<identifier>'), 'CCI')
        result = cci.get_instance(cci_id)
        result = NestedDict(result)

        t.add_row(['id', result['id']])
        t.add_row(['hostname', result['fullyQualifiedDomainName']])
        t.add_row(['status', FormattedItem(
            result['status']['keyName'] or blank(),
            result['status']['name'] or blank()
        )])
        t.add_row(['state', FormattedItem(
            result['powerState']['keyName'], result['powerState']['name'])])
        t.add_row(['datacenter', result['datacenter']['name']])
        t.add_row([
            'os',
            FormattedItem(
                result['operatingSystem']['softwareLicense']
                ['softwareDescription']['referenceCode'] or blank(),
                result['operatingSystem']['softwareLicense']
                ['softwareDescription']['name'] or blank()
            )])
        t.add_row(['cores', result['maxCpu']])
        t.add_row(['memory', mb_to_gb(result['maxMemory'])])
        t.add_row(['public_ip', result['primaryIpAddress'] or blank()])
        t.add_row(['private_ip', result['primaryBackendIpAddress'] or blank()])
        t.add_row(['private_only', result['privateNetworkOnlyFlag']])
        t.add_row(['private_cpu', result['dedicatedAccountHostOnlyFlag']])
        t.add_row(['created', result['createDate']])
        t.add_row(['modified', result['modifyDate']])

        vlan_table = Table(['type', 'number', 'id'])
        for vlan in result['networkVlans']:
            vlan_table.add_row([
                vlan['networkSpace'], vlan['vlanNumber'], vlan['id']])
        t.add_row(['vlans', vlan_table])

        if result.get('notes'):
            t.add_row(['notes', result['notes']])

        if args.get('--price'):
            t.add_row(['price rate', result['billingItem']['recurringFee']])

        if args.get('--passwords'):
            pass_table = Table(['username', 'password'])
            for item in result['operatingSystem']['passwords']:
                pass_table.add_row([item['username'], item['password']])
            t.add_row(['users', pass_table])

        tag_row = []
        for tag in result['tagReferences']:
            tag_row.append(tag['tag']['name'])

        if tag_row:
            t.add_row(['tags', listing(tag_row, separator=',')])

        ptr_domains = client['Virtual_Guest'].\
            getReverseDomainRecords(id=cci_id)

        for ptr_domain in ptr_domains:
            for ptr in ptr_domain['resourceRecords']:
                t.add_row(['ptr', ptr['data']])

        return t


class CreateOptionsCCI(CLIRunnable):
    """
usage: sl cci create-options [options]

Output available available options when creating a CCI

Options:
  --all         Show all options. default if no other option provided
  --datacenter  Show datacenter options
  --cpu         Show CPU options
  --nic         Show NIC speed options
  --disk        Show disk options
  --os          Show operating system options
  --memory      Show memory size options
"""
    action = 'create-options'
    options = ['datacenter', 'cpu', 'nic', 'disk', 'os', 'memory']

    @classmethod
    def execute(cls, client, args):
        cci = CCIManager(client)
        result = cci.get_create_options()

        show_all = True
        for opt_name in cls.options:
            if args.get("--" + opt_name):
                show_all = False
                break

        if args['--all']:
            show_all = True

        t = KeyValueTable(['Name', 'Value'])
        t.align['Name'] = 'r'
        t.align['Value'] = 'l'

        if args['--datacenter'] or show_all:
            datacenters = [dc['template']['datacenter']['name']
                           for dc in result['datacenters']]
            t.add_row(['datacenter', listing(datacenters, separator=',')])

        if args['--cpu'] or show_all:
            standard_cpu = filter(
                lambda x: not x['template'].get(
                    'dedicatedAccountHostOnlyFlag', False),
                result['processors'])

            ded_cpu = filter(
                lambda x: x['template'].get(
                    'dedicatedAccountHostOnlyFlag', False),
                result['processors'])

            def cpus_row(c, name):
                cpus = []
                for x in c:
                    cpus.append(str(x['template']['startCpus']))

                t.add_row(['cpus (%s)' % name, listing(cpus, separator=',')])

            cpus_row(ded_cpu, 'private')
            cpus_row(standard_cpu, 'standard')

        if args['--memory'] or show_all:
            memory = [
                str(m['template']['maxMemory']) for m in result['memory']]
            t.add_row(['memory', listing(memory, separator=',')])

        if args['--os'] or show_all:
            op_sys = [
                o['template']['operatingSystemReferenceCode'] for o in
                result['operatingSystems']]

            op_sys = sorted(op_sys)
            os_summary = set()

            for o in op_sys:
                os_summary.add(o[0:o.find('_')])

            for summary in sorted(os_summary):
                t.add_row([
                    'os (%s)' % summary,
                    linesep.join(sorted(filter(
                        lambda x: x[0:len(summary)] == summary, op_sys))
                    )
                ])

        if args['--disk'] or show_all:
            local_disks = filter(
                lambda x: x['template'].get('localDiskFlag', False),
                result['blockDevices'])

            san_disks = filter(
                lambda x: not x['template'].get('localDiskFlag', False),
                result['blockDevices'])

            def block_rows(blocks, name):
                simple = {}
                for block in blocks:
                    b = block['template']['blockDevices'][0]
                    bid = b['device']
                    size = b['diskImage']['capacity']

                    if bid not in simple:
                        simple[bid] = []

                    simple[bid].append(str(size))

                for b in sorted(simple.keys()):
                    t.add_row([
                        '%s disk(%s)' % (name, b),
                        listing(simple[b], separator=',')]
                    )

            block_rows(local_disks, 'local')
            block_rows(san_disks, 'san')

        if args['--nic'] or show_all:
            speeds = []
            for x in result['networkComponents']:
                speed = x['template']['networkComponents'][0]['maxSpeed']
                speeds.append(str(speed))

            speeds = sorted(speeds)

            t.add_row(['nic', listing(speeds, separator=',')])

        return t


class CreateCCI(CLIRunnable):
    """
usage: sl cci create --hostname=HOST --domain=DOMAIN --cpu=CPU --memory=MEMORY
                     (--os=OS | --image=GUID) (--hourly | --monthly) [options]

Order/create a CCI. See 'sl cci create-options' for valid options

Required:
  -H --hostname=HOST  Host portion of the FQDN. example: server
  -D --domain=DOMAIN  Domain portion of the FQDN example: example.com
  -c --cpu=CPU        Number of CPU cores
  -m --memory=MEMORY  Memory in mebibytes (n * 1024)

  -o OS, --os=OS      OS install code. Tip: you can specify <OS>_LATEST
  --image=GUID        Image GUID. See: 'sl image list' for reference

  --hourly            Hourly rate instance type
  --monthly           Monthly rate instance type


Optional:
  -d DC, --datacenter=DC   datacenter shortname (sng01, dal05, ...)
                           Note: Omitting this value defaults to the first
                             available datacenter
  -n MBPS, --network=MBPS  Network port speed in Mbps
  --dedicated              Allocate a dedicated CCI (non-shared host)
  --dry-run, --test        Do not create CCI, just get a quote

  -u --userdata=DATA       User defined metadata string
  -F --userfile=FILE       Read userdata from file
  -i --postinstall=URI     Post-install script to download
                             (Only HTTPS executes, HTTP leaves file in /root)
  -k KEY, --key=KEY        The SSH key to add to the root user
  --private                Forces the CCI to only have access the private
                             network.
  -k KEY, --key=KEY        The SSH key to add to the root user
  --wait=SECONDS           Block until CCI is finished provisioning for up to X
                             seconds before returning.
"""
    action = 'create'
    options = ['confirm']

    @staticmethod
    def execute(client, args):
        cci = CCIManager(client)

        if args['--userdata'] and args['--userfile']:
            raise ArgumentError('[-u | --userdata] not allowed with '
                                '[-F | --userfile]')
        if args['--userfile']:
            if not os.path.exists(args['--userfile']):
                raise ArgumentError(
                    'File does not exist [-u | --userfile] = %s'
                    % args['--userfile'])

        data = {
            "hourly": args['--hourly'],
            "cpus": args['--cpu'],
            "domain": args['--domain'],
            "hostname": args['--hostname'],
            "dedicated": args['--dedicated'],
            "local_disk": True,
            "private": args['--private']
        }

        try:
            memory = int(args['--memory'])
            if memory < 1024:
                memory = memory * 1024
        except ValueError:
            unit = args['--memory'][-1]
            memory = int(args['--memory'][0:-1])
            if unit in ['G', 'g']:
                memory = memory * 1024
            if unit in ['T', 'r']:
                memory = memory * 1024 * 1024

        data["memory"] = memory

        if args['--monthly']:
            data['hourly'] = False

        if args.get('--os'):
            data['os_code'] = args['--os']

        if args.get('--image'):
            data['image_id'] = args['--image']

        if args.get('--datacenter'):
            data['datacenter'] = args['--datacenter']

        if args.get('--network'):
            data['nic_speed'] = args.get('--network')

        if args.get('--userdata'):
            data['userdata'] = args['--userdata']
        elif args.get('--userfile'):
            f = open(args['--userfile'], 'r')
            try:
                data['userdata'] = f.read()
            finally:
                f.close()

        if args.get('--postinstall'):
            data['post_uri'] = args.get('--postinstall')

        # Get the SSH key
        if args.get('--key'):
            key_id = resolve_id(SshKeyManager(client).resolve_ids,
                                args.get('--key'), 'SshKey')
            data['ssh_key'] = key_id

        t = Table(['Item', 'cost'])
        t.align['Item'] = 'r'
        t.align['cost'] = 'r'

        if args.get('--test'):
            result = cci.verify_create_instance(**data)
            total_monthly = 0.0
            total_hourly = 0.0
            for price in result['prices']:
                total_monthly += float(price.get('recurringFee', 0.0))
                total_hourly += float(price.get('hourlyRecurringFee', 0.0))
                if args.get('--hourly'):
                    rate = "%.2f" % float(price['hourlyRecurringFee'])
                else:
                    rate = "%.2f" % float(price['recurringFee'])

                t.add_row([price['item']['description'], rate])

            if args.get('--hourly'):
                total = total_hourly
            else:
                total = total_monthly

            billing_rate = 'monthly'
            if args.get('--hourly'):
                billing_rate = 'hourly'
            t.add_row(['Total %s cost' % billing_rate, "%.2f" % total])
            output = SequentialOutput()
            output.append(t)
            output.append(FormattedItem(
                '',
                ' -- ! Prices reflected here are retail and do not '
                'take account level discounts and are not guarenteed.')
            )

        elif args['--really'] or confirm(
                "This action will incur charges on your account. Continue?"):
            result = cci.create_instance(**data)

            t = KeyValueTable(['name', 'value'])
            t.align['name'] = 'r'
            t.align['value'] = 'l'
            t.add_row(['id', result['id']])
            t.add_row(['created', result['createDate']])
            t.add_row(['guid', result['globalIdentifier']])
            output = t
        else:
            raise CLIAbort('Aborting CCI order.')

        if args.get('--wait') or 0 and not args.get('--test'):
            ready = cci.wait_for_transaction(
                result['id'], int(args.get('--wait') or 1))
            t.add_row(['ready', ready])

        return output


class ReadyCCI(CLIRunnable):
    """
usage: sl cci ready <identifier> [options]

Check if a CCI is ready.

Optional:
  --wait=SECONDS  Block until CCI is finished provisioning for up to X seconds
                    before returning.
"""
    action = 'ready'

    @staticmethod
    def execute(client, args):
        cci = CCIManager(client)

        cci_id = resolve_id(cci.resolve_ids, args.get('<identifier>'), 'CCI')
        ready = cci.wait_for_transaction(cci_id, int(args.get('--wait') or 0))

        if ready:
            return "READY"
        else:
            raise CLIAbort("Instance %s not ready" % cci_id)


class ReloadCCI(CLIRunnable):
    """
usage: sl cci reload <identifier> [options]

Reload the OS on a CCI based on its current configuration

Optional:
    -i, --postinstall=URI   Post-install script to download
                             (Only HTTPS executes, HTTP leaves file in /root)
"""

    action = 'reload'
    options = ['confirm']

    @staticmethod
    def execute(client, args):
        cci = CCIManager(client)
        cci_id = resolve_id(cci.resolve_ids, args.get('<identifier>'), 'CCI')
        if args['--really'] or no_going_back(cci_id):
            cci.reload_instance(cci_id, args['--postinstall'])
        else:
            CLIAbort('Aborted')


class CancelCCI(CLIRunnable):
    """
usage: sl cci cancel <identifier> [options]

Cancel a CCI
"""

    action = 'cancel'
    options = ['confirm']

    @staticmethod
    def execute(client, args):
        cci = CCIManager(client)
        cci_id = resolve_id(cci.resolve_ids, args.get('<identifier>'), 'CCI')
        if args['--really'] or no_going_back(cci_id):
            cci.cancel_instance(cci_id)
        else:
            CLIAbort('Aborted')


class ManageCCI(CLIRunnable):
    """
usage: sl cci manage poweroff <identifier> [--cycle | --soft] [options]
       sl cci manage reboot <identifier> [--cycle | --soft] [options]
       sl cci manage poweron <identifier> [options]
       sl cci manage pause <identifier> [options]
       sl cci manage resume <identifier> [options]

Manage active CCI
"""
    action = 'manage'
    options = ['confirm']

    @classmethod
    def execute(cls, client, args):
        if args['poweroff']:
            return cls.exec_shutdown(client, args)

        if args['reboot']:
            return cls.exec_reboot(client, args)

        if args['poweron']:
            return cls.exec_poweron(client, args)

        if args['pause']:
            return cls.exec_pause(client, args)

        if args['resume']:
            return cls.exec_resume(client, args)

    @staticmethod
    def exec_shutdown(client, args):
        vg = client['Virtual_Guest']
        cci = CCIManager(client)
        cci_id = resolve_id(cci.resolve_ids, args.get('<identifier>'), 'CCI')
        if args['--soft']:
            result = vg.powerOffSoft(id=cci_id)
        elif args['--cycle']:
            result = vg.powerCycle(id=cci_id)
        else:
            result = vg.powerOff(id=cci_id)

        return FormattedItem(result)

    @staticmethod
    def exec_poweron(client, args):
        vg = client['Virtual_Guest']
        cci = CCIManager(client)
        cci_id = resolve_id(cci.resolve_ids, args.get('<identifier>'), 'CCI')
        return vg.powerOn(id=cci_id)

    @staticmethod
    def exec_pause(client, args):
        vg = client['Virtual_Guest']
        cci = CCIManager(client)
        cci_id = resolve_id(cci.resolve_ids, args.get('<identifier>'), 'CCI')
        return vg.pause(id=cci_id)

    @staticmethod
    def exec_resume(client, args):
        vg = client['Virtual_Guest']
        cci = CCIManager(client)
        cci_id = resolve_id(cci.resolve_ids, args.get('<identifier>'), 'CCI')
        return vg.resume(id=cci_id)

    @staticmethod
    def exec_reboot(client, args):
        vg = client['Virtual_Guest']
        cci = CCIManager(client)
        cci_id = resolve_id(cci.resolve_ids, args.get('<identifier>'), 'CCI')
        if args['--cycle']:
            result = vg.rebootHard(id=cci_id)
        elif args['--soft']:
            result = vg.rebootSoft(id=cci_id)
        else:
            result = vg.rebootDefault(id=cci_id)

        return result


class NetworkCCI(CLIRunnable):
    """
usage: sl cci network port <identifier> --speed=SPEED (--public | --private)
                           [options]

Manage network settings

Options:
    --speed=SPEED  Port speed. 0 disables the port.
                   [Options: 0, 10, 100, 1000, 10000]
    --public       Public network
    --private      Private network
"""
    action = 'network'

    @classmethod
    def execute(cls, client, args):
        if args['port']:
            return cls.exec_port(client, args)

        if args['details']:
            return cls.exec_detail(client, args)

    @staticmethod
    def exec_port(client, args):
        public = True
        if args['--private']:
            public = False

        cci = CCIManager(client)
        cci_id = resolve_id(cci.resolve_ids, args.get('<identifier>'), 'CCI')

        result = cci.change_port_speed(cci_id, public, args['--speed'])
        if result:
            return "Success"
        else:
            return result

    @staticmethod
    def exec_detail(client, args):
        # TODO this should print out default gateway and stuff
        raise CLIAbort('Not implemented')


class CCIDNS(CLIRunnable):
    """
usage: sl cci dns sync <identifier> [options]

DNS related actions for a CCI

Options:
  -a, -A        Sync only the A record
  --ptr, --PTR  Sync only the PTR record
"""
    action = 'dns'
    options = ['confirm']

    @classmethod
    def execute(cls, client, args):
        if args['sync']:
            return cls.dns_sync(client, args)

    @staticmethod
    def dns_sync(client, args):
        from SoftLayer import DNSManager, DNSZoneNotFound
        dns = DNSManager(client)
        cci = CCIManager(client)

        def sync_a_record():
            #hostname = instance['fullyQualifiedDomainName']
            records = dns.search_record(
                instance['domain'],
                instance['hostname'],
            )

            if not records:
                # don't have a record, lets add one to the base zone
                dns.create_record(
                    zone['id'],
                    instance['hostname'],
                    'a',
                    instance['primaryIpAddress'],
                    ttl=7200)
            else:
                recs = filter(lambda x: x['type'].lower() == 'a', records)
                if len(recs) != 1:
                    raise CLIAbort("Aborting A record sync, found %d "
                                   "A record exists!" % len(recs))
                rec = recs[0]
                rec['data'] = instance['primaryIpAddress']
                dns.edit_record(rec)

        def sync_ptr_record():
            host_rec = instance['primaryIpAddress'].split('.')[-1]
            ptr_domains = client['Virtual_Guest'].\
                getReverseDomainRecords(id=instance['id'])[0]
            edit_ptr = None
            for ptr in ptr_domains['resourceRecords']:
                if ptr['host'] == host_rec:
                    edit_ptr = ptr
                    break

            if edit_ptr:
                edit_ptr['data'] = instance['fullyQualifiedDomainName']
                dns.edit_record(edit_ptr)
            else:
                dns.create_record(
                    ptr_domains['id'],
                    host_rec,
                    'ptr',
                    instance['fullyQualifiedDomainName'],
                    ttl=7200)

        cci_id = resolve_id(cci.resolve_ids, args.get('<identifier>'), 'CCI')
        instance = cci.get_instance(cci_id)

        if not instance['primaryIpAddress']:
            raise CLIAbort('No primary IP address associated with this CCI')

        try:
            zone = dns.get_zone(instance['domain'])
        except DNSZoneNotFound:
            raise CLIAbort("Unable to create A record, "
                           "no zone found matching: %s" % instance['domain'])

        go_for_it = args['--really'] or confirm(
            "Attempt to update DNS records for %s"
            % instance['fullyQualifiedDomainName'])

        if not go_for_it:
            raise CLIAbort("Aborting DNS sync")

        both = False
        if not args.get('--PTR') and not args.get('-A'):
            both = True

        if both or args.get('-A'):
            sync_a_record()

        if both or args.get('--PTR'):
            sync_ptr_record()


class EditCCI(CLIRunnable):
    """
usage: sl cci edit <identifier> [options]

Edit CCI details

Options:
  -H --hostname=HOST  Host portion of the FQDN. example: server
  -D --domain=DOMAIN  Domain portion of the FQDN example: example.com
  -u --userdata=DATA  User defined metadata string
  -F --userfile=FILE  Read userdata from file
"""
    action = 'edit'

    @staticmethod
    def execute(client, args):
        data = {}

        if args['--userdata'] and args['--userfile']:
            raise ArgumentError('[-u | --userdata] not allowed with '
                                '[-F | --userfile]')
        if args['--userfile']:
            if not os.path.exists(args['--userfile']):
                raise ArgumentError(
                    'File does not exist [-u | --userfile] = %s'
                    % args['--userfile'])

        if args.get('--userdata'):
            data['userdata'] = args['--userdata']
        elif args.get('--userfile'):
            f = open(args['--userfile'], 'r')
            try:
                data['userdata'] = f.read()
            finally:
                f.close()

        data['hostname'] = args.get('--hostname')
        data['domain'] = args.get('--domain')

        cci = CCIManager(client)
        cci_id = resolve_id(cci.resolve_ids, args.get('<identifier>'), 'CCI')
        if not cci.edit(cci_id, **data):
            raise CLIAbort("Failed to update CCI")
