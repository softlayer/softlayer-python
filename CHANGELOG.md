# Change Log

## [5.2.9] - TBD
 - Changes: https://github.com/softlayer/softlayer-python/compare/v5.2.8...master
 
#### Added to CLI
* block volume-set-lun-id

## [5.2.8] - 2017-07-19
 - Changes: https://github.com/softlayer/softlayer-python/compare/v5.2.7...master
 
 * Resolved https://github.com/softlayer/softlayer-python/issues/835
 * Resolved https://github.com/softlayer/softlayer-python/issues/826
 * Fix dedicated/private VSI price retrieval for upgrades
 
#### Added to CLI
* block access-password

## [5.2.7] - 2017-06-22
 - Changes: https://github.com/softlayer/softlayer-python/compare/v5.2.6...v5.2.7

Adds support for duplicating block and file storage volumes. Only works on Storage as a Service volumes (Volumes that support encryption at rest). 

#### Added to CLI
 * [block|file] volume-duplicate

## [5.2.6] - 2017-05-22
 - Changes: https://github.com/softlayer/softlayer-python/compare/v5.2.5...v5.2.6
 
#### Added To CLI
* ipsec list
* ipsec detail
* ipsec configure
* ipsec update
* ipsec subnet-add
* ipsec subnet-remove
* ipsec translation-add
* ipsec translation-remove
* ipsec translation-update


## [5.2.5] - 2017-05-05
 - Changes: https://github.com/softlayer/softlayer-python/compare/v5.2.1...v5.2.5
 
The SoftLayer_Network_Storage::storageTierLevel relational property changed in https://softlayer.github.io/release_notes/20170503/ , this version fixes problems caused by that.

### Changed
 - https://github.com/softlayer/softlayer-python/issues/818
 - https://github.com/softlayer/softlayer-python/pull/817
 
## [5.2.4] - 2017-04-06
 - Changes: https://github.com/softlayer/softlayer-python/compare/v5.2.3...v5.2.4
 
### Changed
Removed some debug code that was accidently added in the pypi release
 
## [5.2.3] - 2017-04-05
 - Changes: https://github.com/softlayer/softlayer-python/compare/v5.2.2...v5.2.3

### Added
 - Adds Python 3.6 support

### Changed
 - CLI+API: Removes the iSCSI manager and commands
 - API: Fixes hardware order failing to find a single bare metal fast provision package to use

## [5.2.2] - 2017-02-24
 - Changes: https://github.com/softlayer/softlayer-python/compare/v5.2.1...v5.2.2

### Added
 - Adds release process documentation
 - CLI: Displays NFS mount point for volumes in volume list and detail commands
 - CLI+API: Enables `slcli file` and `block` storage commands to order tier 10 endurance storage and replica

### Changed
 - Updates docs to replace `sl` command with `slcli`
 - CLI: Removes requirement to have `--os-type` provided for file storage ordering
 - API: Fixes block storage ordering to handle size provided properly
 - CLI: Fixes load balancer detail output so that JSON output is sane
 - API: Includes check if object storage endpoints were provided by the API before trying to add them to the endpoints returned by `list_endpoints`

## [5.2.1] - 2016-10-4
 - Changes: https://github.com/softlayer/softlayer-python/compare/v5.2.0...v5.2.1

### Added
 - CLI: Adds a new 'jsonraw' format option that will print JSON without whitespace. This is useful for integrating the CLI with other tooling.

### Changed
 - API: Fixes JSON loading while using the REST transport with Python 3
 - CLI+API: Metadata disks are now excluded when capturing "all" block devices with `slcli virtual capture --all`
 - CLI: Fixes a bug where dns zone importing was not importing wildcard records

## [5.2.0] - 2016-08-25
 - Changes: https://github.com/softlayer/softlayer-python/compare/v5.1.0...v5.2.0

### Added
 - CLI+API: Significant additions to `slcli file` and `slcli block` commands. You can now authorize hosts, revoke access. You can also create, delete, restore, disable, enable snapshots. These features need to be battle-tested so report any issues that you see.
 - CLI+API: Adds logic to `SoftLayer.create_client_from_env` that detects if a REST endpoint_url was given in order to use the REST transport automatically. This means that you can also configure REST endpoints for `slcli`. The default still uses XML-RPC endpoint, but from a small amount of testing shows that the REST transport is significantly faster.
 - CLI: Adds `--network-space` to `slcli subnet list` in order to filter subnets based on network space. The two main options are PUBLIC and PRIVATE. For example, to list all public subnets, you can run: `slcli subnet list --network-space=PUBLIC`
 - CLI: Adds a new, non-default column, "created_by" that shows who ordered the volume for `slcli file volume-list` and `slcli block volume-list`.
 - CLI: Adds a new `slcli report bandwidth` command that will print a report of all bandwidth pools and virtual/hardware servers that your user has access to.
 - CLI: Adds an "IN" syntax to the `slcli call-api` command. For example, to find VSIs that are in either the dal05 or sng01 datacenter you can run this command: `slcli call-api Account getVirtualGuests -f 'virtualGuests.datacenter.name IN dal05,sng01'`

### Changed
 - CLI: Fixes a UnicodeEncodeError when piping slcli output with unicode characters. This was mostly reported with `slcli image list` but could also happen with many other calls.
 - CLI: Fixed a bug where os_version was not displaying correctly in `slcli virtual detail` or `slcli virtual detail`

## [5.1.0] - 2016-05-12
 - Changes: https://github.com/softlayer/softlayer-python/compare/v5.0.1...v5.1.0

### Added
 - CLI+API: Added block storage functionality. You can order, list, detail, cancel volumes. You can list and delete snapshots. You can also list ACLs for volumes.
 - Added functionality to attach/detach devices to tickets
 - CLI: Virtual list now lists users and passwords for all known software

### Changed
 - CLI: Fixes bug with `vlan detail` CLI command

## [5.0.1] - 2016-03-30
 - https://github.com/softlayer/softlayer-python/compare/v5.0.0...v5.0.1

### Changed
 - CLI: Adds missing dependency that was previously pulled in by prompt_toolkit
 - API: Fix a bug by updating the CDN manager to use the new purge method
 - CLI: Fixes bug that occured when iscsi listings with resources have no datacenter

## [5.0.0] - 2016-03-18
 - Changes: https://github.com/softlayer/softlayer-python/compare/v4.1.1...v5.0.0

### Added
 - CLI: Adds a shell (accessable with `slcli shell`) which provides autocomplete for slcli commands and options
 - CLI: How filters work with `slcli call-api` has changed significantly. Instead of accepting JSON, it now accepts an easier-to-use format. See `slcli call-api -h` for examples
 - API: Adds manager for object storage
 - API: Improved REST transport support

### Changed
 - CLI: Move modifying nic speed to `slcli virtual edit` and `slcli hardware edit` instead of having its own command
 - CLI: 'virtual' and 'hardware' are preferred over 'vs' and 'server' in the CLI
 - CLI+API: Many unmentioned bug fixes

## [4.1.1] - 2015-08-17
 - Changes: https://github.com/softlayer/softlayer-python/compare/v4.1.0...v4.1.1

### Added
 - CLI: Re-adds `--no-public` option to only provision private interfaces with servers via `slcli server create`

### Changed
 - CLI: Fixes to work with Click v5
 - Removes non-functional `--vlan-public` and `--vlan-private` from `slcli server create`
 - VSManager.wait_for_ready will now behave as it is documented to behave.

## [4.1.0] - 2015-08-17
 - Changes: https://github.com/softlayer/softlayer-python/compare/v4.0.4...v4.1.0

### Added
 - CLI: Adds a shell which provides a shell interface for `slcli`. This is available by using `slcli shell`
 - CLI: `slcli vs create` and `slcli server create` will now prompt for missing required options
 - CLI+API: Adds editing of hardware tags

### Changed
 - CLI: Fixes `slcli firewall add` command
 - CLI: Handles case where `slcli vs detail` and `slcli server detail` was causing an error when trying to display the creator
 - API: Fixes VSManager.verify_create_instance() with tags (and, in turn, `slcli vs create --test` with tags)
 - CLI: Fixes `vs resume` command
 - API+CLI: Updates hardware ordering to deal with location-specific prices
 - CLI: Fixes several description errors in the CLI
 - CLI: Running `vs edit` without a tag option will no longer remove all tags

## [4.0.4] - 2015-06-30
 - Changes: https://github.com/softlayer/softlayer-python/compare/v4.0.3...v4.0.4

### Changed
 - CLI: Fixes bug with pulling the userData property for the virtual server detail
 - CLI: Fixes a class of bugs invloving unicode from the API

## [4.0.3] - 2015-06-15
 - Changes: https://github.com/softlayer/softlayer-python/compare/v4.0.2...v4.0.3

### Changed
 - CLI: Fixes bug with `slcli vs ready` command
 - CLI: Fixes bug with `slcli loadbal service-add` command
 - CLI: Fixes bug with `slcli vlan list` with vlans that don't have a datacenter
 - CLI: Improves validation of virtual server and hardware create commands

## [4.0.2] - 2015-05-04
 - Changes https://github.com/softlayer/softlayer-python/compare/v4.0.1...v4.0.2

### Changed
 - CLI: Fixes a bug that breaks user confirmation prompts
 - CLI: Fixes general issue with sorting on certain row types in the CLI
 - API: Fixes image capture for Windows guests

## [4.0.1] - 2015-04-28
 - Changes: https://github.com/softlayer/softlayer-python/compare/v4.0.0...v4.0.1

### Changed
 - CLI: Fixes bug in `sl setup` command not properly defaulting to current values.
 - API: Fixes bug where turning off compression headers would still send compression headers.
 - CLI: Reverts to using ids over global identifiers for `sl vs list` and `sl server list`.

## [4.0.0] - 2015-04-21
 - Changes: https://github.com/softlayer/softlayer-python/compare/v3.3.0...v4.0.0
 - Because there are many changes between version 3 and version 4, it is strongly recommend to pin the version of the SoftLayer python bindings as soon as you can in order to prevent unintentional breakage when upgrading. To keep yourself on version 3, you can use this directive: softlayer>=3,<4. That can be used with pip (pip install softlayer>=3,<4), requirements in your setup.py and/or in your requirements.txt file.

### Added
 - API: The client transport is now pluggable. If you want to add extra logging or accounting, you can now subclass or wrap softlayer.transports.XmlRpcTransport in order to do so. A good example of that is done with softlayer.transports.TimingTransport.
 - API+CLI: Adds ability to import virtual images from a given URI. The API only supports importing from a swift account using 'swift://'. For more details, see http://developer.softlayer.com/reference/services/SoftLayer_Virtual_Guest_Block_Device_Template_Group/createFromExternalSource.
 - CLI: A `--fixtures` global flag was added to pull from fixture data instead of the API. This is useful for discovery, demonstration and testing purposes.
 - CLI: A `--verbose` or `-v` flag was added to eventually replace `--debug`. To make a command more verbose, simply add more `-v` flags. For example `sl -vvv vs list` will be the most verbose and show everything down to request/response tracing.
 - CLI: Credentials can now be requested using `sl vs credentials <identifier>`, `sl hardware credentials <identifier>` and `sl nas credentials <identifier>` for virtual servers, hardware servers and NAS accounts respectively.
 - CLI: Adds virtual server rescue command, `sl vs rescue <identifier>`

### Changed
 - CLI: The command is renamed from `sl` to `slcli` to avoid package conflicts.
 - CLI: Global options now need to be specified right after the `slcli` command. For example, you would now use `slcli --format=raw list` over `slcli vs list --format=raw`. This is a change for the following options:
   - --format
   - -c or --config
   - --debug
   - --proxy
   - -y or --really
   - --version
 - API: The hardware manager has a significant update to how place_order() works. It will now only support the fast server provisioning package which has presets for options like CPU, Memory and disk.
 - API: Removed deprecated SoftLayer.CCIManager.
 - API: Adds virtual server rescue command to SoftLayer.VSManager
 - CLI: Significant changes were done to the CLI argument parsing. Docopt was dropped in favor of click. Therefore, some subtle differences which aren't documented here may exist.

## [3.3.0] - 2014-10-23
 - Changes: https://github.com/softlayer/softlayer-python/compare/v3.2.0...v3.3.0

### Added
 - CLI+API: Load balancer support
 - CLI: More detail added to the `sl image detail` and `sl image list` commands
 - CLI: Adds command to import DNS entries from BIND zone files
 - CLI+API: Adds support for booting into rescue images for virtual servers and hardware
 - API: Adds ability to order virtual and hardare servers from a quote to the ordering manager

### Changed
 - CLI: Fixes bug with `sl server list-chassis` and `sl server list-chassis`
 - API: Restructure of the way custom authentication can be plugged in the API client
 - Several other bug fixes

## [3.2.0] - 2014-07-09
 - Changes: https://github.com/softlayer/softlayer-python/compare/v3.1.0...v3.2.0

### Added
 - CLI+API: Added firewall manager and CLI module
 - CLI+API: Added iscsi manager and CLI module
 - API: Added ability to create multiple virtual servers at once to VSManager
 - API: Added OrderingManager. Remove hard-coded price IDs

### Changed
 - Fixed several small bugs

## [3.1.0] - 2014-04-24
 - Changes: https://github.com/softlayer/softlayer-python/compare/v3.0.2...v3.1.0

### Added
 - CLI+API: Added CDN manager and CLI module
 - CLI+API: Added ticket manager and CLI module
 - CLI+API: Added image manager and improves image CLI module
 - CLI+API: Added the ability to specify a proxy URL for API bindings and the CLI
 - CLI+API: Added ability to resize a virtual machine
 - CLI+API: Added firewall manager and CLI module
 - CLI+API: Added load balancer manager and CLI module

### Changed
 - API: six is now used to provide support for Python 2 and Python 3 with the same source
 - CLI+API: Implemented product name changes in accordance with SoftLayer's new product names. Existing managers should continue to work as before. Minor CLI changes were necessary.
 - Many bug fixes and minor suggested improvements

## [3.0.2] - 2013-12-9
 - Changes: https://github.com/softlayer/softlayer-python/compare/v3.0.1...v3.0.2

### Added
 - CLI+API: Simplified object mask reformatting and added support for more complex masks.
 - CLI+API: Added IPMI IP address to hardware details.
 - CLI: Added support for ordering multiple disks when creating a CCI.
 - API: Added flag to disable compression on HTTP requests.
 - CLI: Added CIDR information to subnet displays.

### Changed
 - CLI: Fixed the sl bmc create --network argument.
 - CLI+API: Improved output of the message queue feature and fixed some minor bugs.
 - CLI: Fixed an error when using --test and ordering a non-private subnet.
 - API: Fix to prevent double counting results in summary_by_datacenter().

### [3.0.1] - 2013-10-11
 - Changes: https://github.com/softlayer/softlayer-python/compare/v3.0.0...v3.0.1

### Added
 - CLI+API: Added ability to specify SSH keys when reloading CCIs and servers.

### Changed
 - CLI: Fixed an error message about pricing information that appeared when ordering a new private subnet.

## [3.0.0] - 2013-09-19
 - Changes: https://github.com/softlayer/softlayer-python/compare/v2.3.0...v3.0.0

### Added
 - CLI+API: Adds SoftLayer Message Queue Service bindings (as a manager) and a CLI counterpart. With this you can interact with existing message queue accounts
 - CLI+API: Adds the ability to create CCIs with the following options: metadata, post-install script, SSH key
 - CLI+API: Improved dedicated server ordering. Adds power management for hardware servers: power-on, power-off, power-cycle, reboot
 - CLI+API: Adds a networking manager and adds several network-related CLI modules. This includes the ability to:
   - list, create, cancel and assign global IPs
   - list, create, cancel and detail subnets. Also has the ability to lookup details about an IP address with 'sl subnet lookup'
   - list, detail VLANs
   - show and edit RWhois data
 - CLI+API: Ability to manage SSH Keys with a manager and a CLI module
 - CLI: Adds a --debug option to print out debugging information. --debug=3 is the highest log level which prints full HTTP request/responses including the body
 - CLI+API: Adds the ability to create hardware servers with a default SSH key
 - CLI: Adds templating for creating CCIs and hardware nodes which can be used to create more CCIs and hardware with the same settings

### Changed
 - Many bug fixes and consistency improvements
 - API: Removes old API client interfaces which have been deprecated in the v2. See link for more details: https://softlayer-api-python-client.readthedocs.org/en/latest/api/client/#backwards-compatibility
 - CLI: The commands in the main help are now organized into categories

## [2.3.0] - 2013-07-19
 - Changes: https://github.com/softlayer/softlayer-python/compare/v2.2.0...v2.3.0

### Added
 - CLI+API: Added much more hardware support: Filters for hardware listing, dedicated server/bare metal cloud ordering, hardware cancellation
 - CLI+API: Added DNS Zone filtering (server side)
 - CLI+API: Added Post Install script support for CCIs and hardware
 - CLI: Added Message queue functionality
 - CLI: Added --debug option to CLI commands
 - API: Added more logging
 - API: Added token-based auth so you can use the API bindings with your username/password if you want. (It's still highly recommended to use your API key instead of your password)

### Changed
 - Several bug fixes and improvements
 - Removed Python 2.5 support. Some stuff MIGHT work with 2.5 but it is no longer tested
 - API: Refactored managers into their own module to not clutter the top level

## [2.2.0] - 2013-04-11
### Added
 - Added sphinx documentation. See it here: https://softlayer-api-python-client.readthedocs.org
 - CCI: Adds Support for Additional Disks
 - CCI: Adds a way to block until transactions are done on a CCI
 - CLI: For most CCI commands, you can specify id, hostname, private ip or public ip as <identifier>
 - CLI: Adds the ability to filter list results for CCIs
 - API: for large result sets, requests can now be chunked into smaller batches on the server side. Using service.iter_call('getObjects', ...) or service.getObjects(..., iter=True) will return a generator regardless of the results returned. offset and limit can be passed in like normal. An additional named parameter of 'chunk' is used to limit the number of items coming back in a single request, defaults to 100

### Changed
 - Consistency changes/bug fixes
