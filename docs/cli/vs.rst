.. _vs_user_docs:
  
Working with Virtual Servers
============================
Using the SoftLayer portal for ordering virtual servers is fine, but for a number of reasons it's sometimes to use the command-line. For this, you can use the SoftLayer command-line client to make administrative tasks quicker and easier. This page gives an intro to working with SoftLayer virtual servers using the SoftLayer command-line client.

.. note::

	The following assumes that the client is already :ref:`configured with valid SoftLayer credentials<cli>`.


First, let's list the current virtual servers with `sl vs list`.
::

	$ sl vs list
	:....:............:......:.......:........:............:............:....................:
	: id : datacenter : host : cores : memory : primary_ip : backend_ip : active_transaction :
	:....:............:......:.......:........:............:............:....................:
	:....:............:......:.......:........:............:............:....................:

We don't have any virtual servers! Let's fix that. Before we can create a VS, we need to know what options are available to me: RAM, CPU, operating systems, disk sizes, disk types, datacenters. Luckily, there's a simple command to do that, `sl vs create-options`.

::

	$ sl vs create-options
	:.................:..............................................................................................:
	:            Name : Value                                                                                        :
	:.................:..............................................................................................:
	:      datacenter : ams01,dal01,dal05,sea01,sjc01,sng01,wdc01                                                    :
	:  cpus (private) : 1,2,4,8                                                                                      :
	: cpus (standard) : 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16                                                       :
	:          memory : 1024,2048,3072,4096,5120,6144,7168,8192,9216,10240,11264,12288,13312,14336,15360,16384,32768 :
	:     os (CENTOS) : CENTOS_5_32                                                                                  :
	:                 : CENTOS_5_64                                                                                  :
	:                 : CENTOS_6_32                                                                                  :
	:                 : CENTOS_6_64                                                                                  :
	: os (CLOUDLINUX) : CLOUDLINUX_5_32                                                                              :
	:                 : CLOUDLINUX_5_64                                                                              :
	:                 : CLOUDLINUX_6_32                                                                              :
	:                 : CLOUDLINUX_6_64                                                                              :
	:     os (DEBIAN) : DEBIAN_5_32                                                                                  :
	:                 : DEBIAN_5_64                                                                                  :
	:                 : DEBIAN_6_32                                                                                  :
	:                 : DEBIAN_6_64                                                                                  :
	:                 : DEBIAN_7_32                                                                                  :
	:                 : DEBIAN_7_64                                                                                  :
	:     os (REDHAT) : REDHAT_5_64                                                                                  :
	:                 : REDHAT_6_32                                                                                  :
	:                 : REDHAT_6_64                                                                                  :
	:     os (UBUNTU) : UBUNTU_10_32                                                                                 :
	:                 : UBUNTU_10_64                                                                                 :
	:                 : UBUNTU_12_32                                                                                 :
	:                 : UBUNTU_12_64                                                                                 :
	:                 : UBUNTU_8_32                                                                                  :
	:                 : UBUNTU_8_64                                                                                  :
	:   os (VYATTACE) : VYATTACE_6.5_64                                                                              :
	:        os (WIN) : WIN_2003-DC-SP2-1_32                                                                         :
	:                 : WIN_2003-DC-SP2-1_64                                                                         :
	:                 : WIN_2003-ENT-SP2-5_32                                                                        :
	:                 : WIN_2003-ENT-SP2-5_64                                                                        :
	:                 : WIN_2003-STD-SP2-5_32                                                                        :
	:                 : WIN_2003-STD-SP2-5_64                                                                        :
	:                 : WIN_2008-DC-R2_64                                                                            :
	:                 : WIN_2008-DC-SP2_32                                                                           :
	:                 : WIN_2008-DC-SP2_64                                                                           :
	:                 : WIN_2008-ENT-R2_64                                                                           :
	:                 : WIN_2008-ENT-SP2_32                                                                          :
	:                 : WIN_2008-ENT-SP2_64                                                                          :
	:                 : WIN_2008-STD-R2-SP1_64                                                                       :
	:                 : WIN_2008-STD-R2_64                                                                           :
	:                 : WIN_2008-STD-SP2_32                                                                          :
	:                 : WIN_2008-STD-SP2_64                                                                          :
	:                 : WIN_2012-DC_64                                                                               :
	:                 : WIN_2012-STD_64                                                                              :
	:                 : WIN_7-ENT_32                                                                                 :
	:                 : WIN_7-PRO_32                                                                                 :
	:                 : WIN_8-ENT_64                                                                                 :
	:   local disk(0) : 25,100                                                                                       :
	:   local disk(2) : 25,100,150,200,300                                                                           :
	:     san disk(0) : 25,100                                                                                       :
	:     san disk(2) : 10,20,25,30,40,50,75,100,125,150,175,200,250,300,350,400,500,750,1000,1500,2000              :
	:     san disk(3) : 10,20,25,30,40,50,75,100,125,150,175,200,250,300,350,400,500,750,1000,1500,2000              :
	:     san disk(4) : 10,20,25,30,40,50,75,100,125,150,175,200,250,300,350,400,500,750,1000,1500,2000              :
	:     san disk(5) : 10,20,25,30,40,50,75,100,125,150,175,200,250,300,350,400,500,750,1000,1500,2000              :
	:             nic : 10,100,1000                                                                                  :
	:.................:..............................................................................................:

Here's the command to create a 2-core, 1G memory, Ubuntu 12.04 hourly instance in the San Jose datacenter using the command `sl vs create`.

::

	$ sl vs create --host=example --domain=softlayer.com -c 2 -m 1024 -o UBUNTU_12_64 --hourly --datacenter sjc01
	This action will incur charges on your account. Continue? [y/N]: y
	:.........:......................................:
	:    name : value                                :
	:.........:......................................:
	:      id : 1234567                              :
	: created : 2013-06-13T08:29:44-06:00            :
	:    guid : 6e013cde-a863-46ee-8s9a-f806dba97c89 :
	:.........:......................................:


With the last command, the virtual server has begun being created. It should instantly appear in your listing now.

::

	$ sl vs list
	:.........:............:.......................:.......:........:................:..............:....................:
	:    id   : datacenter :          host         : cores : memory :   primary_ip   :  backend_ip  : active_transaction :
	:.........:............:.......................:.......:........:................:..............:....................:
	: 1234567 :   sjc01    : example.softlayer.com :   2   :   1G   : 108.168.200.11 : 10.54.80.200 :    Assign Host     :
	:.........:............:.......................:.......:........:................:..............:....................:

Cool. You may ask "It's creating... but how do I know when it's done?". Well, here's how:

::

	$ sl vs ready 'example' --wait=600
	READY

When the previous command returns, I know that the virtual server has finished the provisioning process and is ready to use. This is *very* useful for chaining commands together. Now that you have your virtual server, let's get access to it. To do that, use the `sl vs detail` command. From the example below, you can see that the username is 'root' and password is 'ABCDEFGH'.

.. warning::

	Be careful when using the `--passwords` flag. This will print the password to the virtual server onto the screen. Make sure no one is looking over your shoulder. It's also advisable to change your root password soon after creating your virtual server.

::

	$ sl vs detail example --passwords
	:..............:...........................:
	:         Name : Value                     :
	:..............:...........................:
	:           id : 1234567                   :
	:     hostname : example.softlayer.com     :
	:       status : Active                    :
	:        state : Running                   :
	:   datacenter : sjc01                     :
	:        cores : 2                         :
	:       memory : 1G                        :
	:    public_ip : 108.168.200.11            :
	:   private_ip : 10.54.80.200              :
	:           os : Ubuntu                    :
	: private_only : False                     :
	:  private_cpu : False                     :
	:      created : 2013-06-13T08:29:44-06:00 :
	:     modified : 2013-06-13T08:31:57-06:00 :
	:        users : root ABCDEFGH             :
	:..............:...........................:


There are many other commands to help manage virtual servers. To see them all, use `sl help vs`.

::
	
	$ sl help vs
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

	For several commands, <identifier> will be asked for. This can be the id,
	hostname or the ip address for a virtual server.

	Standard Options:
	  -h --help  Show this screen
