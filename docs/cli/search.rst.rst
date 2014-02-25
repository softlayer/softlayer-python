.. _search_usr_docs:

Working with Search
====================================
Using the SoftLayer portal or API to find things/objects and their data is simple if you know where
to go. If you are having trouble finding the things or have to go through a lot of things, here comes search. The SLAPI provides a search service to search across some of the commonly used data you need to find. This page gives an intro to working with SoftLayer's Search service using the SoftLayer command-line client.

.. note::

	The following assumes that the client is already :ref:`configured with valid SoftLayer credentials<cli>`.


First, let's list the types of things we can search with `sl search types`.
::

	$ sl search types
	:..............:
	: Type         :
	:..............:
	: hardware     :
	: loadbalancer :
	: ip_address   :
	: vlan         :
	: firewall     :
	: ticket       :
	: cci          :
	:..............:

Now, lets go through some common search scenarios.

Search for hardware and cci in datacenter dal05.

::

	$ sl search -t hardware,cci
	 Search String: dal05
	:.........:...........:......................:
	:    Id   :   Type    : Name                 :
	:.........:...........:......................:
	:   123   :    cci    : app1.example.com     :
	:.........:...........:......................:
	:   345   : hardware  : db1.example.com      :
	:.........:...........:......................:


But I wanted to do it in all one line!

::

	$ sl search -t hardware,cci -s dal05
	:.........:...........:......................:
	:    Id   :   Type    : Name                 :
	:.........:...........:......................:
	:   123   :    cci    : app1.example.com     :
	:.........:...........:......................:
	:   345   : hardware  : db1.example.com      :
	:.........:...........:......................:


Search for hosts with all the same domain.

::

	$ sl search -t hardware,cci -s example.com
	:.........:...........:......................:
	:    Id   :   Type    : Name                 :
	:.........:...........:......................:
	:   123   :    cci    : app1.example.com     :
	:.........:...........:......................:
	:   345   : hardware  : db1.example.com      :
	:.........:...........:......................:

Search for anything associated with server app1.example.com

::

	$ sl search -s app1.example.com
	:.........:............:.........................................:
	:    Id   :    Type    : Name                                    :
	:.........:............:.........................................:
	:   123   :    cci     : app1.example.com                        :
	:   345   : ip_address : 171.102.122.254                         :
	:   456   : ip_address : 2327:ad10:123a:0201:0000:0000:0000:0002 :
	:   567   : ip_address : 10.0.0.1                                :
	:   123   :   ticket   : MONITORING: Network Monitor Alert       :
	:.........:............:.........................................:

We got back the server record (the cci), a public ip (171.102.122.254), a ipv6 ip (2327:ad10:123a:0201:0000:0000:0000:0002 ), a private ip (10.0.0.1 ), and a ticket.

Search for any maintenance tickets.

::

	$ sl search -t ticket -s maintenance
	:.........:........:..............................................................:
	:    Id   :  Type  : Name                                                         :
	:.........:........:..............................................................:
	: 7446314 : ticket : Scheduled Maintenance [6410382] Firmware Upgrades - Multiple :
	:         :        : Routers in DAL05 - DAL05 - 09/26/2013                        :
	:.........:........:..............................................................:


There are many other commands to help limit and search upon this data. To see them all, use `sl help search`.

::

	$ usage: sl search [<command>] [<args>...] [options]

	Search for API data objects

	Examples:
	    sl search
	    sl search types
	    sl search -t cci,ticket
	    sl search -t cci,hardware -s dal05

	The available commands are:
	  None            No command results in a prompt for the search
	                   string that you want to use for the search query.
	  types           List available types to narrow search.

