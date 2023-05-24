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

*Some values were ommitted for brevity*

::

    $ slcli vs create-options
    :................................:.................................................................................:
    :                           name : value                                                                           :
    :................................:.................................................................................:
    :                     datacenter : ams01                                                                           :
    :                                : ams03                                                                           :
    :                                : wdc07                                                                           :
    :             flavors (balanced) : B1_1X2X25                                                                       :
    :                                : B1_1X2X25                                                                       :
    :                                : B1_1X2X100                                                                      :
    :                cpus (standard) : 1,2,4,8,12,16,32,56                                                             :
    :               cpus (dedicated) : 1,2,4,8,16,32,56                                                                :
    :          cpus (dedicated host) : 1,2,4,8,12,16,32,56                                                             :
    :                         memory : 1024,2048,4096,6144,8192,12288,16384,32768,49152,65536,131072,247808            :
    :        memory (dedicated host) : 1024,2048,4096,6144,8192,12288,16384,32768,49152,65536,131072,247808            :
    :                    os (CENTOS) : CENTOS_5_64                                                                     :
    :                                : CENTOS_LATEST_64                                                                :
    :                os (CLOUDLINUX) : CLOUDLINUX_5_64                                                                 :
    :                                : CLOUDLINUX_6_64                                                                 :
    :                                : CLOUDLINUX_LATEST                                                               :
    :                                : CLOUDLINUX_LATEST_64                                                            :
    :                    os (COREOS) : COREOS_CURRENT_64                                                               :
    :                                : COREOS_LATEST                                                                   :
    :                                : COREOS_LATEST_64                                                                :
    :                    os (DEBIAN) : DEBIAN_6_64                                                                     :
    :                                : DEBIAN_LATEST_64                                                                :
    :            os (OTHERUNIXLINUX) : OTHERUNIXLINUX_1_64                                                             :
    :                                : OTHERUNIXLINUX_LATEST                                                           :
    :                                : OTHERUNIXLINUX_LATEST_64                                                        :
    :                    os (REDHAT) : REDHAT_5_64                                                                     :
    :                                : REDHAT_6_64                                                                     :
    :                                : REDHAT_7_64                                                                     :
    :                                : REDHAT_LATEST                                                                   :
    :                                : REDHAT_LATEST_64                                                                :
    :                    san disk(0) : 25,100                                                                          :
    :                    san disk(2) : 10,20,25,30,40,50,75,100,125,150,175,200,250,300,350,400,500,750,1000,1500,2000 :
    :                  local disk(0) : 25,100                                                                          :
    :                  local disk(2) : 25,100,150,200,300                                                              :
    : local (dedicated host) disk(0) : 25,100                                                                          :
    :           nic (dedicated host) : 100,1000                                                                        :
    :................................:.................................................................................:


Here's the command to create a 2-core virtual server with 1GiB memory, running
Ubuntu 14.04 LTS, and that is billed on an hourly basis in the San Jose 1
datacenter using the command `slcli vs create`.

::

    $ slcli vs create --hostname=example --domain=softlayer.com -f B1_1X2X25 -o DEBIAN_LATEST_64  --datacenter=ams01 --billing=hourly
    This action will incur charges on your account. Continue? [y/N]: y
        :..........:.................................:......................................:...........................:
        :    ID    :               FQDN              :                 guid                 :         Order Date        :
        :..........:.................................:......................................:...........................:
        : 70112999 : testtesttest.test.com : 1abc7afb-9618-4835-89c9-586f3711d8ea : 2019-01-30T17:16:58-06:00 :
        :..........:.................................:......................................:...........................:
        :.........................................................................:
        :                            OrderId: 12345678                            :
        :.......:.................................................................:
        :  Cost : Description                                                     :
        :.......:.................................................................:
        :   0.0 : Debian GNU/Linux 9.x Stretch/Stable - Minimal Install (64 bit)  :
        :   0.0 : 25 GB (SAN)                                                     :
        :   0.0 : Reboot / Remote Console                                         :
        :   0.0 : 100 Mbps Public & Private Network Uplinks                       :
        :   0.0 : 0 GB Bandwidth Allotment                                        :
        :   0.0 : 1 IP Address                                                    :
        :   0.0 : Host Ping and TCP Service Monitoring                            :
        :   0.0 : Email and Ticket                                                :
        :   0.0 : Automated Reboot from Monitoring                                :
        :   0.0 : Unlimited SSL VPN Users & 1 PPTP VPN User per account           :
        :   0.0 : 2 GB                                                            :
        :   0.0 : 1 x 2.0 GHz or higher Core                                      :
        : 0.000 : Total hourly cost                                               :
        :.......:.................................................................:


After the last command, the virtual server is now being built. It should
instantly appear in your virtual server list now.

::

    $ slcli vs list
    :.........:............:.......................:.......:........:................:..............:....................:
    :    id   : datacenter :          host         : cores : memory :   primary_ip   :  backend_ip  : active_transaction :
    :.........:............:.......................:.......:........:................:..............:....................:
    : 1234567 :   ams01    : example.softlayer.com :   2   :   1G   : 108.168.200.11 : 10.54.80.200 :    Assign Host     :
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
    :   datacenter : ams01                     :
    :        cores : 2                         :
    :       memory : 1G                        :
    :    public_ip : 108.168.200.11            :
    :   private_ip : 10.54.80.200              :
    :           os : Debian                    :
    : private_only : False                     :
    :  private_cpu : False                     :
    :      created : 2013-06-13T08:29:44-06:00 :
    :     modified : 2013-06-13T08:31:57-06:00 :
    :        users : root ABCDEFGH             :
    :..............:...........................:



.. click:: SoftLayer.CLI.virt.bandwidth:cli
   :prog: virtual bandwidth
   :show-nested:

If no timezone is specified, IMS local time (CST) will be assumed, which might not match your user's selected timezone.


.. click:: SoftLayer.CLI.virt.cancel:cli
   :prog: virtual cancel
   :show-nested:

.. click:: SoftLayer.CLI.virt.capture:cli
   :prog: virtual capture
   :show-nested:

.. click:: SoftLayer.CLI.virt.create:cli
   :prog: virtual create
   :show-nested:

.. click:: SoftLayer.CLI.virt.create_options:cli
   :prog: virtual create-options
   :show-nested:

.. click:: SoftLayer.CLI.virt.dns:cli
   :prog: virtual dns-sync
   :show-nested:

.. click:: SoftLayer.CLI.virt.edit:cli
   :prog: virtual edit
   :show-nested:

.. click:: SoftLayer.CLI.virt.list:cli
   :prog: virtual list
   :show-nested:

.. click:: SoftLayer.CLI.virt.power:pause
   :prog: virtual pause
   :show-nested:


.. click:: SoftLayer.CLI.virt.power:power_on
   :prog: virtual power-on
   :show-nested:


.. click:: SoftLayer.CLI.virt.power:power_off
   :prog: virtual power-off
   :show-nested:

.. click:: SoftLayer.CLI.virt.power:resume
   :prog: virtual resume
   :show-nested:

.. click:: SoftLayer.CLI.virt.power:rescue
   :prog: virtual rescue
   :show-nested:

.. click:: SoftLayer.CLI.virt.power:reboot
   :prog: virtual reboot
   :show-nested:

.. click:: SoftLayer.CLI.virt.ready:cli
   :prog: virtual ready
   :show-nested:

.. click:: SoftLayer.CLI.virt.upgrade:cli
   :prog: virtual upgrade
   :show-nested:

.. click:: SoftLayer.CLI.virt.usage:cli
   :prog: virtual usage
   :show-nested:

.. click:: SoftLayer.CLI.virt.storage:cli
   :prog: virtual storage

.. click:: SoftLayer.CLI.virt.billing:cli
   :prog: virtual billing
   :show-nested:

.. click:: SoftLayer.CLI.virt.detail:cli
   :prog: virtual detail
   :show-nested:

.. click:: SoftLayer.CLI.virt.reload:cli
   :prog: virtual reload
   :show-nested:

.. click:: SoftLayer.CLI.virt.credentials:cli
   :prog: virtual credentials
   :show-nested:

.. click:: SoftLayer.CLI.virt.migrate:cli
   :prog: virtual migrate
   :show-nested:

.. click:: SoftLayer.CLI.virt.authorize_storage:cli
   :prog: virtual authorize-storage
   :show-nested:

.. click:: SoftLayer.CLI.virt.monitoring:cli
   :prog: virtual monitoring
   :show-nested:

.. click:: SoftLayer.CLI.virt.access:cli
   :prog: virtual access
   :show-nested:

.. click:: SoftLayer.CLI.virt.notifications:cli
   :prog: virtual notifications
   :show-nested:

.. click:: SoftLayer.CLI.virt.notification_add:cli
   :prog: virtual notification-add
   :show-nested:

.. click:: SoftLayer.CLI.virt.notification_delete:cli
   :prog: virtual notification-delete
   :show-nested:

.. click:: SoftLayer.CLI.dedicatedhost.list:cli 
   :prog: virtual host-list
   :show-nested:

.. click:: SoftLayer.CLI.dedicatedhost.create:cli
   :prog: virtual host-create

.. click:: SoftLayer.CLI.virt.os_available:cli
   :prog: virtual os-available
   :show-nested:

Manages the migration of virutal guests. Supports migrating virtual guests on Dedicated Hosts as well.

Reserved Capacity
-----------------
.. toctree::
    :maxdepth: 2

    vs/reserved_capacity

Placement Groups
----------------
.. toctree::
    :maxdepth: 2

    vs/placement_group

