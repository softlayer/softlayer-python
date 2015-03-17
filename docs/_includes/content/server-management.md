# Introduction 

This section is a blended "how to" and "FAQ" for creating and working with virtual servers. Several examples are real user scenarios, whereas others are simply usage examples. Included are the following:

<div class="container">
<div class="row">
<div class="col-lg-4 col-md-4">
<li><a href="#toc_2">List Virtual Servers</a></li>
<li><a href="#toc_3">See Available Options</a></li>
<li><a href="#toc_4">Create a Virtual Server</a></li>
<li><a href="#toc_5">Check Status</a></li>
</div>

<div class="col-lg-4 col-md-4">
<li><a href="#toc_6">Access a Virtual Server</a></li>
<li><a href="#toc_8">Edit a Virtual Server</a></li>
<li><a href="#toc_9">Reload a Virtual Server</a></li>
<li><a href="#toc_10">Cancel a Virtual Server</a></li>
</div>
</div>
</div>

***
# User Scenarios

Below are individual scenarios for creating and managing virtual servers.

## List Virtual Servers

Run `sl vs list` to generate a list of current virtual servers. In this example, the CLI spits out an empty list.

<section class="panel example">
```bash
$ sl vs list

:....:............:......:.......:........:............:............:....................:
: id : datacenter : host : cores : memory : primary_ip : backend_ip : active_transaction :
:....:............:......:.......:........:............:............:....................:
:....:............:......:.......:........:............:............:....................:
```
</section>


## See Available Options

Before we can create a virtual server, we need to know what options are available. This includes:

* <a href="http://www.softlayer.com/data-centers" target="_blank">Data Centers</a>
* Cores (CPUs)
* RAM (Memory)
* OS (Operating Systems)
* Storage types (local disk, SAN disk)
* Storage size

Luckily, there’s a command for that. Run `sl vs create-options` to see what options are available.

<section class="panel example">
```bash
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
```
</section>


## Create a Virtual Server

Looking at our options, we'll make a virtual server with the following server options:

* 2 cores
* 1024MB of RAM
* Ubuntu 12.04 (64-bit)
* Hourly subscription
* San Jose datacenter

| Server Component | Server Option         | CLI Option     | CLI Value      |
| ---------------- | --------------------- | -------------- | -------------- |
| Cores            | 2 cores               |  `-c`          | `2`            |
| RAM              | 1024MB (1GB)          | `-m`           | `1024`         |
| OS               | Ubuntu 12.04 (64-bit) | `-o`           | `UBUNTU_12_64` |
| Subscription     | Hourly                | `--[option]`   | `hourly`       |
| Data Center      | San Jose              | `--datacenter` | `scj01`        |

> Go to [Additional Options](#toc_12) for a list of all options/flags.

The command we'll use begins with the CLI option, followed by the CLI value:

<section class="panel example">
```
-c 2 -m 1024 -o UBUNTU_12_64 --hourly --datacenter sjc01
```
</section>

In this example:

* `-c 2` is _2_ _c_ores (CPUs)
* `-m 1024` is _1024_MB (1GB) of _m_emory (or RAM)
* `-o UBUNTU_12_64` is the _Ubuntu 12_.04 (_64_-bit) _o_perating system
* `--hourly` is an _hourly_ subscription
* `--datacenter sjc01` is the location of our _sjc01_ San Jose _data center_ (optional)

> All of these options are required except Datacenter. If you do not provide a Datacenter, our system will pick the first available.

Run `sl vs create`, followed by your hostname, domain, and these commands to create the virtual server.

<section class="panel example">
```bash
$ sl vs create --host=example --domain=softlayer.com -c 2 -m 1024 -o UBUNTU_12_64 --hourly --datacenter sjc01

This action will incur charges on your account. Continue? [y/N]: y
:.........:......................................:
:    name : value                                :
:.........:......................................:
:      id : 1234567                              :
: created : 2013-06-13T08:29:44-06:00            :
:    guid : 6e013cde-a863-46ee-8s9a-f806dba97c89 :
:.........:......................................:
```
</section>

After running `sl vs create`, a new virtual server will spin up. If you run `sl vs list` again, it should instantly appear in your list.

<section class="panel example">
```bash
$ sl vs list

:.........:............:.......................:.......:........:................:..............:....................:
:    id   : datacenter :          host         : cores : memory :   primary_ip   :  backend_ip  : active_transaction :
:.........:............:.......................:.......:........:................:..............:....................:
: 1234567 :   sjc01    : example.softlayer.com :   2   :   1G   : 108.168.200.11 : 10.54.80.200 :    Assign Host     :
:.........:............:.......................:.......:........:................:..............:....................:
```
</section>


## Check Status

Run the following command to see if your virtual server is ready to use.

<section class="panel example">
```bash
$ sl vs ready 'example' --wait=600
READY
```
</section>

The "READY" status indicates that the virtual server has finished the provisioning process and is ready to use.


## Access a Virtual Server

Now that we have a virtual server, we need access to it. To do this, run `sl vs detail [host]`. The CLI will show the basic details about the virtual server.

Do note that the CLI does not show the password. This is for your security. In order to retrieve the password, run `sl vs detail [host] --passwords`. In the example below, our username is "root" and password is "ABCDEFGH".

<section class="panel example">
```bash
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
```
</section>

> Be careful when using the `-–passwords` option. This prints the password onto your screen, which others might see. In addition, we recommend that you change your password immediately after creating your virtual server.

***
# Usage Examples

Below are examples that demonstrate how to manage virtual servers.

## Edit a Virtual Server

You can edit several details for each individual virtual server, such as the domain and hostname. Run `sl vs edit --help` to see usage examples.

```bash
$ sl vs edit --help
usage: sl vs edit <identifier> [options]

Edit a virtual server's details

Options:
  -D --domain=DOMAIN  Domain portion of the FQDN example: example.com
  -F --userfile=FILE  Read userdata from file
  -H --hostname=HOST  Host portion of the FQDN. example: server
  -u --userdata=DATA  User defined metadata string
```

## Reload a Virtual Server

You can reload the OS for a virtual server based on its current configuration. Run `sl vs reload --help` to see usage examples.

```bash
$ sl vs reload --help
usage: sl vs reload <identifier> [--key=KEY...] [options]

Reload the OS on a virtual server based on its current configuration

Optional:
  -i, --postinstall=URI  Post-install script to download
                           (Only HTTPS executes, HTTP leaves file in /root)
  -k, --key=KEY          SSH keys to add to the root user. Can be specified
                           multiple times
```

## Cancel a Virtual Server

In addition to ordering a virtual server, you can also use the CLI to cancel one. Run `sl vs cancel --help` to see usage examples.

```bash
$ sl vs cancel --help
usage: sl vs cancel <identifier> [options]

Cancel a virtual server
```

***
# Additional Commands

There are a number of other commands to help manage your virtual servers. To see them all, run `sl help vs`.

```bash
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
```

***
# Additional Options

Below is a list of options to use for ordering/creating your virtual servers. To see them all, run `sl vs create --help`.

```bash
$ sl vs create --help
usage: sl vs create [--disk=SIZE...] [--key=KEY...] [options]

Order/create a VS. See 'sl vs create-options' for valid options

Required:
  -c, --cpu=CPU          Number of CPU cores
  -D, --domain=DOMAIN    Domain portion of the FQDN. example: example.com
  -H, --hostname=HOST    Host portion of the FQDN. example: server
  --image=GUID           Image GUID. See: 'sl image list' for reference
  -m, --memory=MEMORY    Memory in mebibytes. example: 2048
  -o, --os=OS            OS install code. Tip: you can specify <OS>_LATEST

  --hourly               Hourly rate instance type
  --monthly              Monthly rate instance type


Optional:
  -d, --datacenter=DC    Datacenter shortname (sng01, dal05, ...)
                         Note: Omitting this value defaults to the first
                           available datacenter
  --dedicated            Create a dedicated VS (Virtual Server (Private Node))
  --san                  Use SAN storage instead of local disk. Applies to
                           all disks specified with --disk.
  --test                 Do not create VS, just get a quote
  --export=FILE          Exports options to a template file
  -F, --userfile=FILE    Read userdata from file
  -i, --postinstall=URI  Post-install script to download
                           (Only HTTPS executes, HTTP leaves file in /root)
  -k, --key=KEY          SSH keys to add to the root user. Can be specified
                           multiple times
  --like=IDENTIFIER      Use the configuration from an existing VS
  -n, --network=MBPS     Network port speed in Mbps
  --disk=SIZE...         Disks. Can be specified multiple times
  --private              Forces the VS to only have access the private network
  -t, --template=FILE    A template file that defaults the command-line
                           options using the long name in INI format
  -u, --userdata=DATA    User defined metadata string
  --vlan_public=VLAN     The ID of the public VLAN on which you want the VS
                           placed.
  --vlan_private=VLAN    The ID of the private VLAN on which you want the VS
                           placed.
  --wait=SECONDS         Block until VS is finished provisioning for up to X
                           seconds before returning
```
