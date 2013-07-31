.. _cli:

Command-line Interface
======================

The SoftLayer command line interface is available via the `sl` command available in your `PATH`.  The `sl` command is a reference implementation of SoftLayer API bindings for python and how to efficiently make API calls. See the :ref:`usage-examples` section to see how to discover all of the functionality not fully documented here.

.. toctree::
   :maxdepth: 2

   cli/cci
   cli/dev


Configuration Setup
-------------------
To check the configuration, you can use `sl config show`.
::

	$ sl config setup
	Username: username
	API Key: oyVmeipYQCNrjVS4rF9bHWV7D75S6pa1fghFl384v7mwRCbHTfuJ8qRORIqoVnha
	Endpoint URL [https://api.softlayer.com/xmlrpc/v3/]: 
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


Configuration File Details
--------------------------
The CLI loads your settings from a number of different locations.

* Enviorment variables (SL_USERNAME, SL_API_KEY)
* Config file (~/.softlayer)
* Or argument (-C/path/to/config or --config=/path/to/config)

The configuration file is INI based and requires the `softlayer` section to be present. 
The only required fields are `username` and `api_key`. You can optionally also/exclusively supply the `endpoint_url` as well.

*Full config*
::

	[softlayer]
	username = username
	api_key = oyVmeipYQCNrjVS4rF9bHWV7D75S6pa1fghFl384v7mwRCbHTfuJ8qRORIqoVnha
	endpoint_url = https://api.softlayer.com/xmlrpc/v3/

*exclusive url*
::

	[softlayer]
	endpoint_url = https://api.softlayer.com/xmlrpc/v3/

.. _usage-examples:

Usage Examples
--------------
To discover the available commands, simply type `sl`.
::

	$ sl
	usage: sl <command> [<args>...]
	       sl help <command>
	       sl [-h | --help]

	SoftLayer Command-line Client

	The available commands are:
	  firewall  Firewall rule and security management
	  image     Manages compute and flex images
	  ssl       Manages SSL
	  cci       Manage, delete, order compute instances
	  dns       Manage DNS
	  config    View and edit configuration for this tool
	  metadata  Get details about this machine. Also available with 'my' and 'meta'
	  nas       View NAS details
	  iscsi     View iSCSI details

	See 'sl help <command>' for more information on a specific command.

	To use most commands your SoftLayer username and api_key need to be configured.
	The easiest way to do that is to use: 'sl config setup'

As you can see, there are a number of commands. To look at the list of subcommands for Cloud Compute Instances, type `sl <command>`. For example:
::

	$ sl cci
	usage: sl cci [<command>] [<args>...] [options]

	Manage, delete, order compute instances

	The available commands are:
	  network         Manage network settings
	  create          Order and create a CCI
	                    (see `sl cci create-options` for choices)
	  manage          Manage active CCI
	  list            List CCI's on the account
	  detail          Output details about a CCI
	  dns             DNS related actions to a CCI
	  cancel          Cancel a running CCI
	  create-options  Output available available options when creating a CCI
	  reload          Reload the OS on a CCI based on its current configuration

	Standard Options:
	  -h --help  Show this screen

Finally, we can make an actual call. Let's list out the CCIs on our account using `sl cci list`.

::

	$ sl cci list
	:.........:............:....................:.......:........:................:..............:....................:
	:    id   : datacenter :       host         : cores : memory :   primary_ip   :  backend_ip  : active_transaction :
	:.........:............:....................:.......:........:................:..............:....................:
	: 1234567 :   dal05    :  test.example.com  :   4   :   4G   :    12.34.56    :   65.43.21   :         -          :
	:.........:............:....................:.......:........:................:..............:....................:

Most commands will take in additional options/arguments. To see all available actions, use `--help`.
::

	$ sl cci list --help
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
