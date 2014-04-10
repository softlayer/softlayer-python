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
	usage: sl <module> [<args>...]
	       sl help <module>
	       sl help <module> <command>
	       sl [-h | --help]
	
	SoftLayer Command-line Client
	
	Compute:
	  image     Manages compute and flex images
	  metadata  Get details about this machine. Also available with 'my' and 'meta'
	  server    Bare metal servers
	  sshkey    Manage SSH keys on your account
	  vs        Virtual Servers (formerly CCIs)

	Networking:
	  cdn        Content Delivery Network service management
	  dns        Domain Name System
	  firewall   Firewall rule and security management
	  globalip   Global IP address management
	  messaging  Message Queue Service
	  rwhois     RWhoIs operations
	  ssl        Manages SSL
	  subnet     Subnet ordering and management
	  vlan       Manage VLANs on your account

	Storage:
	  iscsi     View iSCSI details
	  nas       View NAS details

	General:
	  config    View and edit configuration for this tool
	  ticket    Manage account tickets
	  summary   Display an overall summary of your account
	  help      Show help

	See 'sl help <module>' for more information on a specific module.

	To use most commands your SoftLayer username and api_key need to be configured.
	The easiest way to do that is to use: 'sl config setup'

As you can see, there are a number of commands. To look at the list of subcommands for Cloud Compute Instances, type `sl <command>`. For example:
::

	$ sl vs
	usage: sl vs [<command>] [<args>...] [options]

	Manage, delete, order compute instances

	The available commands are:
	  cancel          Cancel a running virtual server
	  capture         Create an image the disk(s) of a virtual server
	  create          Order and create a virtual server
	                    (see sl vs create-options for choices)
	  create-options  Output available available options when creating a VS
	  detail          Output details about a virtual server
	  dns             DNS related actions to a virtual server
	  edit            Edit details of a virtual server
	  list            List virtual servers on the account
	  nic-edit        Edit NIC settings
	  pause           Pauses an active virtual server
	  power-off       Powers off a running virtual server
	  power-on        Boots up a virtual server
	  ready           Check if a virtual server has finished provisioning
	  reboot          Reboots a running virtual server
	  reload          Reload the OS on a VS based on its current configuration
	  resume          Resumes a paused virtual server
	  upgrade         Upgrades parameters of a virtual server

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
	usage: sl vs list [--hourly | --monthly] [--sortby=SORT_COLUMN] [--tags=TAGS]
	                  [options]

	List virtual servers

	Examples:
	    sl vs list --datacenter=dal05
	    sl vs list --network=100 --cpu=2
	    sl vs list --memory='>= 2048'
	    sl vs list --tags=production,db

	Options:
	  --sortby=ARG  Column to sort by. options: id, datacenter, host,
	                Cores, memory, primary_ip, backend_ip

	Filters:
	  --hourly                 Show hourly instances
	  --monthly                Show monthly instances
	  -H --hostname=HOST       Host portion of the FQDN. example: server
	  -D --domain=DOMAIN       Domain portion of the FQDN example: example.com
	  -c --cpu=CPU             Number of CPU cores
	  -m --memory=MEMORY       Memory in mebibytes (n * 1024)
	  -d DC, --datacenter=DC   datacenter shortname (sng01, dal05, ...)
	  -n MBPS, --network=MBPS  Network port speed in Mbps
	  --tags=ARG               Only show instances that have one of these tags.
	                           Comma-separated. (production,db)

	For more on filters see 'sl help filters'

	Standard Options:
	  --format=ARG           Output format. [Options: table, raw] [Default: table]
	  -C FILE --config=FILE  Config file location. [Default: ~/.softlayer]
	  -h --help              Show this screen
