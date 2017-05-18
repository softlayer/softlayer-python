.. _cli:

Command-line Interface
======================

The SoftLayer command line interface is available via the `slcli` command
available in your `PATH`.  The `slcli` command is a reference implementation of
SoftLayer API bindings for python and how to efficiently make API calls. See
the :ref:`usage-examples` section to see how to discover all of the
functionality not fully documented here.

.. toctree::
   :maxdepth: 2

   cli/ipsec
   cli/vs


.. _config_setup:

Configuration Setup
-------------------
To update the configuration, you can use `slcli setup`.
::

	$ slcli setup
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
	Are you sure you want to write settings to "/home/me/.softlayer"? [y/N]: y

To check the configuration, you can use `slcli config show`.
::

	$ slcli config show
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
To discover the available commands, simply type `slcli`.
::

	$ slcli
        Usage: slcli [OPTIONS] COMMAND [ARGS]...
        
          SoftLayer Command-line Client
        
        Options:
          --format [table|raw|json|jsonraw]
                                          Output format  [default: table]
          -C, --config PATH               Config file location  [default:
                                          ~/.softlayer]
          -v, --verbose                   Sets the debug noise level, specify multiple
                                          times for more verbosity.
          --proxy TEXT                    HTTP[S] proxy to be use to make API calls
          -y, --really / --not-really     Confirm all prompt actions
          --demo / --no-demo              Use demo data instead of actually making API
                                          calls
          --version                       Show the version and exit.
          -h, --help                      Show this message and exit.
        
        Commands:
          block           Block Storage.
          call-api        Call arbitrary API endpoints.
          cdn             Content Delivery Network.
          config          CLI configuration.
          dns             Domain Name System.
          file            File Storage.
          firewall        Firewalls.
          globalip        Global IP addresses.
          hardware        Hardware servers.
          image           Compute images.
          loadbal         Load balancers.
          messaging       Message queue service.
          metadata        Find details about this machine.
          nas             Network Attached Storage.
          object-storage  Object Storage.
          report          Reports.
          rwhois          Referral Whois.
          setup           Edit configuration.
          shell           Enters a shell for slcli.
          sshkey          SSH Keys.
          ssl             SSL Certificates.
          subnet          Network subnets.
          summary         Account summary.
          ticket          Support tickets.
          virtual         Virtual Servers.
          vlan            Network VLANs.
        
          To use most commands your SoftLayer username and api_key need to be
          configured. The easiest way to do that is to use: 'slcli setup'

As you can see, there are a number of commands/sections. To look at the list of
subcommands for virtual servers type `slcli vs`. For example:
::

	$ slcli vs
	Usage: slcli vs [OPTIONS] COMMAND [ARGS]...

	  Virtual Servers.

	Options:
	  --help  Show this message and exit.

	Commands:
	  cancel          Cancel virtual servers.
	  capture         Capture SoftLayer image.
	  create          Order/create virtual servers.
	  create-options  Virtual server order options.
	  credentials     List virtual server credentials.
	  detail          Get details for a virtual server.
	  dns-sync        Sync DNS records.
	  edit            Edit a virtual server's details.
	  list            List virtual servers.
	  network         Manage network settings.
	  pause           Pauses an active virtual server.
	  power_off       Power off an active virtual server.
	  power_on        Power on a virtual server.
	  ready           Check if a virtual server is ready.
	  reboot          Reboot an active virtual server.
	  reload          Reload operating system on a virtual server.
	  rescue          Reboot into a rescue image.
	  resume          Resumes a paused virtual server.
	  upgrade         Upgrade a virtual server.

Finally, we can make an actual call. Let's list out the virtual servers on our
account by using `slcli vs list`.

::

	$ slcli vs list
	:.........:............:....................:.......:........:................:..............:....................:
	:    id   : datacenter :       host         : cores : memory :   primary_ip   :  backend_ip  : active_transaction :
	:.........:............:....................:.......:........:................:..............:....................:
	: 1234567 :   sjc01    :  test.example.com  :   4   :   4G   :    12.34.56    :   65.43.21   :         -          :
	:.........:............:....................:.......:........:................:..............:....................:

Most commands will take in additional options/arguments. To see all available actions, use `--help`.
::

	$ slcli vs list --help
	Usage: slcli vs list [OPTIONS]

	  List virtual servers.

	Options:
	  --sortby [guid|hostname|primary_ip|backend_ip|datacenter]
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
