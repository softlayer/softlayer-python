.. _cli:

Command-line Interface
======================

The SoftLayer command line interface is available via the `sl` command available in your `PATH`.  The `sl` command is a reference implementation of SoftLayer API bindings for python and how to efficiently make API calls. See the :ref:`usage-examples` section to see how to discover all of the functionality not fully documented here.

.. toctree::
   :maxdepth: 2

   cli/vs


.. _config_setup:

Configuration Setup
-------------------
To update the configuration, you can use `sl config setup`.
::

	$ sl config setup
	Username []: username
	API Key or Password []:
	Endpoint (public|private|custom): public
	:..............:..................................................................:
	:         Name : Value                                                            :
	:..............:..................................................................:
	:     Username : username                                                         :
	:      API Key : oyVmeipYQCNrjVS4rF9bHWV7D75S6pa1fghFl384v7mwRCbHTfuJ8qRORIqoVnha :
	: Endpoint URL : https://api.softlayer.com/xmlrpc/v3/                             :
	:..............:..................................................................:
	Are you sure you want to write settings to "/path/to/home/.softlayer"? [y/N]: y

To check the configuration, you can use `sl config show`.
::

	$ sl config show
	:..............:..................................................................:
	:         Name : Value                                                            :
	:..............:..................................................................:
	:     Username : username                                                         :
	:      API Key : oyVmeipYQCNrjVS4rF9bHWV7D75S6pa1fghFl384v7mwRCbHTfuJ8qRORIqoVnha :
	: Endpoint URL : https://api.softlayer.com/xmlrpc/v3/                             :
	:..............:..................................................................:


To see more about the config file format, see :ref:`config_file`.

.. _usage-examples:

Usage Examples
--------------
To discover the available commands, simply type `sl`.
::

	$ sl
	Usage: sl [OPTIONS] COMMAND [ARGS]...

	  SoftLayer Command-line Client

	Options:
	  --format [table|raw|json]  Output format
	  -C, --config PATH          Config file location
	  --debug [0|1|2|3]          Sets the debug noise level
	  -v, --verbose              Sets the debug noise level
	  --timings                  Time each API call and display after results
	  --proxy TEXT               HTTP[S] proxy to be use to make API calls
	  -y, --really               Confirm all prompt actions
	  --fixtures                 Use fixtures instead of actually making API calls
	  --version                  Show the version and exit.
	  --help                     Show this message and exit.

	Commands:
	  cdn        Content Delivery Network
	  config     CLI configuration
	  dns        Domain Name System
	  firewall   Firewalls
	  globalip   Global IP addresses
	  image      Compute images
	  iscsi      iSCSI storage
	  loadbal    Load balancers
	  messaging  Message queue service
	  metadata   Find details about this machine
	  nas        Network Attached Storage
	  rwhois     Referral Whois
	  server     Hardware servers
	  snapshot   Snapshots
	  sshkey     SSH Keys
	  ssl        SSL Certificates
	  subnet     Network subnets
	  summary    Display summary information about the account
	  ticket     Support tickets
	  vlan       Network VLANs
	  vs         Virtual Servers

	  To use most commands your SoftLayer username and api_key need to be
	  configured. The easiest way to do that is to use: 'sl config setup'

As you can see, there are a number of commands. To look at the list of subcommands for Cloud Compute Instances, type `sl <command>`. For example:
::

	$ sl vs
	Usage: sl vs [OPTIONS] COMMAND [ARGS]...

	  Virtual Servers

	Options:
	  --help  Show this message and exit.

	Commands:
	  cancel          Cancel virtual servers
	  capture         Capture SoftLayer image
	  create          Order/create virtual servers
	  create-options  Virtual server order options
	  detail          Get details for a virtual server
	  dns-sync        Sync DNS records
	  edit            Edit a virtual server's details
	  list            List virtual servers
	  network         Manage network settings
	  pause           Pauses an active virtual server
	  power_off       Power off an active virtual server
	  power_on        Power on a virtual server
	  ready           Check if a virtual server is ready
	  reload          Reload operating system on a virtual server
	  rescue          Reboot into a rescue image
	  resume          Resumes a paused virtual server
	  upgrade         Upgrade a virtual server

Finally, we can make an actual call. Let's list out the virtual servers on our account using `sl vs list`.

::

	$ sl vs list
	:.........:............:....................:.......:........:................:..............:....................:
	:    id   : datacenter :       host         : cores : memory :   primary_ip   :  backend_ip  : active_transaction :
	:.........:............:....................:.......:........:................:..............:....................:
	: 1234567 :   dal05    :  test.example.com  :   4   :   4G   :    12.34.56    :   65.43.21   :         -          :
	:.........:............:....................:.......:........:................:..............:....................:

Most commands will take in additional options/arguments. To see all available actions, use `--help`.
::

	$ sl vs list --help
		Usage: sl vs list [OPTIONS]

	  List virtual servers

	Options:
	  --sortby [id|datacenter|host|cores|memory|primary_ip|backend_ip]
	                                  Column to sort by
	  -c, --cpu INTEGER               Number of CPU cores
	  -D, --domain TEXT               Domain portion of the FQDN
	  -d, --datacenter TEXT           Datacenter shortname
	  -H, --hostname TEXT             Host portion of the FQDN
	  -m, --memory INTEGER            Memory in mebibytes
	  -n, --network TEXT              Network port speed in Mbps
	  --hourly                        Show only hourly instances
	  --monthly                       Show only monthly instances
	  --tags TEXT                     Show instances that have one of these comma-
	                                  separated tags
	  --help                          Show this message and exit.
