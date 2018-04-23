.. _vs_user_docs:

Working with Virtual Servers
============================
Using the SoftLayer portal to order virtual servers is fine, but for a number
of reasons it's often more convenient to use the command line. For this, you
can use SoftLayer's command-line client to make administrative tasks quicker
and easier. This page gives an intro to working with SoftLayer virtual servers
using SoftLayer's command-line client.

.. note::

	The following assumes that the client is already
	:ref:`configured with valid SoftLayer credentials<cli>`.


First, let's list the current virtual servers with `slcli vs list`.
::

	$ slcli vs list
	:.....:............:.........................:.......:........:..............:.............:....................:........:
	:  id : datacenter :           host          : cores : memory :  primary_ip  :  backend_ip : active_transaction : owner  :
	:.....:............:.........................:.......:........:..............:.............:....................:........:
	:.....:............:.........................:.......:........:..............:.............:....................:........:

We don't have any virtual servers yet! Let's fix that. Before we can create a
virtual server (VS), we need to know what options are available to us: RAM,
CPU, operating systems, disk sizes, disk types, datacenters, and so on.
Luckily, there's a simple command to show all options: `slcli vs create-options`.

::

	$ slcli vs create-options
	:................................:.................................................................................:
	:                           name : value                                                                           :
	:................................:.................................................................................:
	:                     datacenter : ams01                                                                           :
	:                                : ams03                                                                           :
	:                                : che01                                                                           :
	:                                : dal01                                                                           :
	:                                : dal05                                                                           :
	:                                : dal06                                                                           :
	:                                : dal09                                                                           :
	:                                : dal10                                                                           :
	:                                : dal12                                                                           :
	:                                : dal13                                                                           :
	:                                : fra02                                                                           :
	:                                : hkg02                                                                           :
	:                                : hou02                                                                           :
	:                                : lon02                                                                           :
	:                                : lon04                                                                           :
	:                                : lon06                                                                           :
	:                                : mel01                                                                           :
	:                                : mex01                                                                           :
	:                                : mil01                                                                           :
	:                                : mon01                                                                           :
	:                                : osl01                                                                           :
	:                                : par01                                                                           :
	:                                : sao01                                                                           :
	:                                : sea01                                                                           :
	:                                : seo01                                                                           :
	:                                : sjc01                                                                           :
	:                                : sjc03                                                                           :
	:                                : sjc04                                                                           :
	:                                : sng01                                                                           :
	:                                : syd01                                                                           :
	:                                : syd04                                                                           :
	:                                : tok02                                                                           :
	:                                : tor01                                                                           :
	:                                : wdc01                                                                           :
	:                                : wdc04                                                                           :
	:                                : wdc06                                                                           :
	:                                : wdc07                                                                           :
	:             flavors (balanced) : B1_1X2X25                                                                       :
	:                                : B1_1X2X25                                                                       :
	:                                : B1_1X2X100                                                                      :
	:                                : B1_1X2X100                                                                      :
	:                                : B1_1X4X25                                                                       :
	:                                : B1_1X4X25                                                                       :
	:                                : B1_1X4X100                                                                      :
	:                                : B1_1X4X100                                                                      :
	:                                : B1_2X4X25                                                                       :
	:                                : B1_2X4X25                                                                       :
	:                                : B1_2X4X100                                                                      :
	:                                : B1_2X4X100                                                                      :
	:                                : B1_2X8X25                                                                       :
	:                                : B1_2X8X25                                                                       :
	:                                : B1_2X8X100                                                                      :
	:                                : B1_2X8X100                                                                      :
	:                                : B1_4X8X25                                                                       :
	:                                : B1_4X8X25                                                                       :
	:                                : B1_4X8X100                                                                      :
	:                                : B1_4X8X100                                                                      :
	:                                : B1_4X16X25                                                                      :
	:                                : B1_4X16X25                                                                      :
	:                                : B1_4X16X100                                                                     :
	:                                : B1_4X16X100                                                                     :
	:                                : B1_8X16X25                                                                      :
	:                                : B1_8X16X25                                                                      :
	:                                : B1_8X16X100                                                                     :
	:                                : B1_8X16X100                                                                     :
	:                                : B1_8X32X25                                                                      :
	:                                : B1_8X32X25                                                                      :
	:                                : B1_8X32X100                                                                     :
	:                                : B1_8X32X100                                                                     :
	:                                : B1_16X32X25                                                                     :
	:                                : B1_16X32X25                                                                     :
	:                                : B1_16X32X100                                                                    :
	:                                : B1_16X32X100                                                                    :
	:                                : B1_16X64X25                                                                     :
	:                                : B1_16X64X25                                                                     :
	:                                : B1_16X64X100                                                                    :
	:                                : B1_16X64X100                                                                    :
	:                                : B1_32X64X25                                                                     :
	:                                : B1_32X64X25                                                                     :
	:                                : B1_32X64X100                                                                    :
	:                                : B1_32X64X100                                                                    :
	:                                : B1_32X128X25                                                                    :
	:                                : B1_32X128X25                                                                    :
	:                                : B1_32X128X100                                                                   :
	:                                : B1_32X128X100                                                                   :
	:                                : B1_48X192X25                                                                    :
	:                                : B1_48X192X25                                                                    :
	:                                : B1_48X192X100                                                                   :
	:                                : B1_48X192X100                                                                   :
	: flavors (balanced local - hdd) : BL1_1X2X100                                                                     :
	:                                : BL1_1X4X100                                                                     :
	:                                : BL1_2X4X100                                                                     :
	:                                : BL1_2X8X100                                                                     :
	:                                : BL1_4X8X100                                                                     :
	:                                : BL1_4X16X100                                                                    :
	:                                : BL1_8X16X100                                                                    :
	:                                : BL1_8X32X100                                                                    :
	:                                : BL1_16X32X100                                                                   :
	:                                : BL1_16X64X100                                                                   :
	:                                : BL1_32X64X100                                                                   :
	:                                : BL1_32X128X100                                                                  :
	:                                : BL1_56X242X100                                                                  :
	: flavors (balanced local - ssd) : BL2_1X2X100                                                                     :
	:                                : BL2_1X4X100                                                                     :
	:                                : BL2_2X4X100                                                                     :
	:                                : BL2_2X8X100                                                                     :
	:                                : BL2_4X8X100                                                                     :
	:                                : BL2_4X16X100                                                                    :
	:                                : BL2_8X16X100                                                                    :
	:                                : BL2_8X32X100                                                                    :
	:                                : BL2_16X32X100                                                                   :
	:                                : BL2_16X64X100                                                                   :
	:                                : BL2_32X64X100                                                                   :
	:                                : BL2_32X128X100                                                                  :
	:                                : BL2_56X242X100                                                                  :
	:              flavors (compute) : C1_1X1X25                                                                       :
	:                                : C1_1X1X25                                                                       :
	:                                : C1_1X1X100                                                                      :
	:                                : C1_1X1X100                                                                      :
	:                                : C1_2X2X25                                                                       :
	:                                : C1_2X2X25                                                                       :
	:                                : C1_2X2X100                                                                      :
	:                                : C1_2X2X100                                                                      :
	:                                : C1_4X4X25                                                                       :
	:                                : C1_4X4X25                                                                       :
	:                                : C1_4X4X100                                                                      :
	:                                : C1_4X4X100                                                                      :
	:                                : C1_8X8X25                                                                       :
	:                                : C1_8X8X25                                                                       :
	:                                : C1_8X8X100                                                                      :
	:                                : C1_8X8X100                                                                      :
	:                                : C1_16X16X25                                                                     :
	:                                : C1_16X16X25                                                                     :
	:                                : C1_16X16X100                                                                    :
	:                                : C1_16X16X100                                                                    :
	:                                : C1_32X32X25                                                                     :
	:                                : C1_32X32X25                                                                     :
	:                                : C1_32X32X100                                                                    :
	:                                : C1_32X32X100                                                                    :
	:               flavors (memory) : M1_1X8X25                                                                       :
	:                                : M1_1X8X25                                                                       :
	:                                : M1_1X8X100                                                                      :
	:                                : M1_1X8X100                                                                      :
	:                                : M1_2X16X25                                                                      :
	:                                : M1_2X16X25                                                                      :
	:                                : M1_2X16X100                                                                     :
	:                                : M1_2X16X100                                                                     :
	:                                : M1_4X32X25                                                                      :
	:                                : M1_4X32X25                                                                      :
	:                                : M1_4X32X100                                                                     :
	:                                : M1_4X32X100                                                                     :
	:                                : M1_8X64X25                                                                      :
	:                                : M1_8X64X25                                                                      :
	:                                : M1_8X64X100                                                                     :
	:                                : M1_8X64X100                                                                     :
	:                                : M1_16X128X25                                                                    :
	:                                : M1_16X128X25                                                                    :
	:                                : M1_16X128X100                                                                   :
	:                                : M1_16X128X100                                                                   :
	:                                : M1_30X240X25                                                                    :
	:                                : M1_30X240X25                                                                    :
	:                                : M1_30X240X100                                                                   :
	:                                : M1_30X240X100                                                                   :
	:                  flavors (GPU) : AC1_8X60X25                                                                     :
	:                                : AC1_8X60X100                                                                    :
	:                                : AC1_16X120X25                                                                   :
	:                                : AC1_16X120X100                                                                  :
	:                                : ACL1_8X60X100                                                                   :
	:                                : ACL1_16X120X100                                                                 :
	:                cpus (standard) : 1,2,4,8,12,16,32,56                                                             :
	:               cpus (dedicated) : 1,2,4,8,16,32,56                                                                :
	:          cpus (dedicated host) : 1,2,4,8,12,16,32,56                                                             :
	:                         memory : 1024,2048,4096,6144,8192,12288,16384,32768,49152,65536,131072,247808            :
	:        memory (dedicated host) : 1024,2048,4096,6144,8192,12288,16384,32768,49152,65536,131072,247808            :
	:                    os (CENTOS) : CENTOS_5_64                                                                     :
	:                                : CENTOS_6_64                                                                     :
	:                                : CENTOS_7_64                                                                     :
	:                                : CENTOS_LATEST                                                                   :
	:                                : CENTOS_LATEST_64                                                                :
	:                os (CLOUDLINUX) : CLOUDLINUX_5_64                                                                 :
	:                                : CLOUDLINUX_6_64                                                                 :
	:                                : CLOUDLINUX_LATEST                                                               :
	:                                : CLOUDLINUX_LATEST_64                                                            :
	:                    os (COREOS) : COREOS_CURRENT_64                                                               :
	:                                : COREOS_LATEST                                                                   :
	:                                : COREOS_LATEST_64                                                                :
	:                    os (DEBIAN) : DEBIAN_6_64                                                                     :
	:                                : DEBIAN_7_64                                                                     :
	:                                : DEBIAN_8_64                                                                     :
	:                                : DEBIAN_9_64                                                                     :
	:                                : DEBIAN_LATEST                                                                   :
	:                                : DEBIAN_LATEST_64                                                                :
	:            os (OTHERUNIXLINUX) : OTHERUNIXLINUX_1_64                                                             :
	:                                : OTHERUNIXLINUX_LATEST                                                           :
	:                                : OTHERUNIXLINUX_LATEST_64                                                        :
	:                    os (REDHAT) : REDHAT_5_64                                                                     :
	:                                : REDHAT_6_64                                                                     :
	:                                : REDHAT_7_64                                                                     :
	:                                : REDHAT_LATEST                                                                   :
	:                                : REDHAT_LATEST_64                                                                :
	:                    os (UBUNTU) : UBUNTU_12_64                                                                    :
	:                                : UBUNTU_14_64                                                                    :
	:                                : UBUNTU_16_64                                                                    :
	:                                : UBUNTU_LATEST                                                                   :
	:                                : UBUNTU_LATEST_64                                                                :
	:                  os (VYATTACE) : VYATTACE_6.5_64                                                                 :
	:                                : VYATTACE_6.6_64                                                                 :
	:                                : VYATTACE_LATEST                                                                 :
	:                                : VYATTACE_LATEST_64                                                              :
	:                       os (WIN) : WIN_2003-DC-SP2-1_32                                                            :
	:                                : WIN_2003-DC-SP2-1_64                                                            :
	:                                : WIN_2003-ENT-SP2-5_32                                                           :
	:                                : WIN_2003-ENT-SP2-5_64                                                           :
	:                                : WIN_2003-STD-SP2-5_32                                                           :
	:                                : WIN_2003-STD-SP2-5_64                                                           :
	:                                : WIN_2008-STD-R2-SP1_64                                                          :
	:                                : WIN_2008-STD-SP2_32                                                             :
	:                                : WIN_2008-STD-SP2_64                                                             :
	:                                : WIN_2012-STD-R2_64                                                              :
	:                                : WIN_2012-STD_64                                                                 :
	:                                : WIN_2016-STD_64                                                                 :
	:                                : WIN_LATEST                                                                      :
	:                                : WIN_LATEST_32                                                                   :
	:                                : WIN_LATEST_64                                                                   :
	:                    san disk(0) : 25,100                                                                          :
	:                    san disk(2) : 10,20,25,30,40,50,75,100,125,150,175,200,250,300,350,400,500,750,1000,1500,2000 :
	:                    san disk(3) : 10,20,25,30,40,50,75,100,125,150,175,200,250,300,350,400,500,750,1000,1500,2000 :
	:                    san disk(4) : 10,20,25,30,40,50,75,100,125,150,175,200,250,300,350,400,500,750,1000,1500,2000 :
	:                    san disk(5) : 10,20,25,30,40,50,75,100,125,150,175,200,250,300,350,400,500,750,1000,1500,2000 :
	:                  local disk(0) : 25,100                                                                          :
	:                  local disk(2) : 25,100,150,200,300                                                              :
	: local (dedicated host) disk(0) : 25,100                                                                          :
	: local (dedicated host) disk(2) : 25,100,150,200,300,400                                                          :
	: local (dedicated host) disk(3) : 25,100,150,200,300,400                                                          :
	: local (dedicated host) disk(4) : 25,100,150,200,300,400                                                          :
	: local (dedicated host) disk(5) : 25,100,150,200,300,400                                                          :
	:                            nic : 10,100,1000                                                                     :
	:           nic (dedicated host) : 100,1000                                                                        :
	:................................:.................................................................................:


Here's the command to create a 2-core virtual server with 1GiB memory, running
Ubuntu 14.04 LTS, and that is billed on an hourly basis in the San Jose 1
datacenter using the command `slcli vs create`.

::

	$ slcli vs create --hostname=example --domain=softlayer.com --cpu 2 --memory 1024 -o UBUNTU_14_64 --datacenter=sjc01 --billing=hourly
	This action will incur charges on your account. Continue? [y/N]: y
	:.........:......................................:
	:    name : value                                :
	:.........:......................................:
	:      id : 1234567                              :
	: created : 2013-06-13T08:29:44-06:00            :
	:    guid : 6e013cde-a863-46ee-8s9a-f806dba97c89 :
	:.........:......................................:


After the last command, the virtual server is now being built. It should
instantly appear in your virtual server list now.

::

	$ slcli vs list
	:.........:............:.......................:.......:........:................:..............:....................:
	:    id   : datacenter :          host         : cores : memory :   primary_ip   :  backend_ip  : active_transaction :
	:.........:............:.......................:.......:........:................:..............:....................:
	: 1234567 :   sjc01    : example.softlayer.com :   2   :   1G   : 108.168.200.11 : 10.54.80.200 :    Assign Host     :
	:.........:............:.......................:.......:........:................:..............:....................:

Cool. You may ask, "It's creating... but how do I know when it's done?" Well,
here's how:

::

	$ slcli vs ready 'example' --wait=600
	READY

When the previous command returns, you'll know that the virtual server has
finished the provisioning process and is ready to use. This is *very* useful
for chaining commands together.

Now that you have your virtual server, let's get access to it. To do that, use
the `slcli vs detail` command. From the example below, you can see that the
username is 'root' and password is 'ABCDEFGH'.

.. warning::

	Be careful when using the `--passwords` flag. This will print the virtual
	server's password on the screen. Make sure no one is looking over your
	shoulder. It's also advisable to change your root password soon after
	creating your virtual server, or to create a user with sudo access and
	disable SSH-based login directly to the root account.

::

	$ slcli vs detail example --passwords
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


There are many other commands to help manage virtual servers. To see them all,
use `slcli help vs`.

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
