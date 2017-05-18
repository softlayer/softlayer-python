.. _cli_ipsec:

Interacting with IPSEC Tunnels
==============================
The IPSEC :ref:`cli` commands can be used to configure an existing IPSEC tunnel context. Subnets in the SoftLayer private network can be associated to the tunnel context along with user-defined remote subnets. Address translation entries may also be defined to provide NAT functionality from static subnet IP addresses associated with the tunnel context to user-defined remote subnet IP addresses.

.. note::

    Most CLI actions that affect an IPSEC tunnel context do not result in configuration changes to SoftLayer network devices. A separate *configure* command is available to issue a device configuration request.

To see more information about the IPSEC tunnel context module and API internaction, see :doc:`IPSEC Module<../api/managers/ipsec>` documentation.

.. _cli_ipsec_list:

ipsec list
----------
A list of all IPSEC tunnel contexts associated with the current user's account can be retrieved via the ``ipsec list`` command. This provides a brief overview of all tunnel contexts and can be used to retrieve an individual context's identifier, which all other CLI commands require.
::

    $ slcli ipsec list
    :.....:..........:...............:..........................:........................:...........................:
    :  id :   name   : friendly name : internal peer IP address : remote peer IP address :          created          :
    :.....:..........:...............:..........................:........................:...........................:
    : 445 : ipsec038 :  ipsec tunnel :      173.192.250.79      :      158.85.80.22      : 2012-03-05T14:07:34-06:00 :
    :.....:..........:...............:..........................:........................:...........................:

.. _cli_ipsec_detail:

ipsec detail
------------
More detailed information can be retrieved for an individual context using the ``ipsec detail`` command. Using the detail command, information about associated internal subnets, remote subnets, static subnets, service subnets and address translations may also be retrieved using multiple instances of the ``-i|--include`` option.
::

    $ slcli ipsec detail 445 -i at -i is -i rs -i sr -i ss
    Context Details:
    :.................................:...........................:
    :                            name : value                     :
    :.................................:...........................:
    :                              id : 445                       :
    :                            name : ipsec038                  :
    :                   friendly name : ipsec tunnel              :
    :        internal peer IP address : 173.192.250.79            :
    :          remote peer IP address : 158.85.80.22              :
    :     advanced configuration flag : 0                         :
    :                   preshared key : secret                    :
    :          phase 1 authentication : MD5                       :
    :    phase 1 diffie hellman group : 0                         :
    :              phase 1 encryption : DES                       :
    :                phase 1 key life : 240                       :
    :          phase 2 authentication : MD5                       :
    :    phase 2 diffie hellman group : 1                         :
    :              phase 2 encryption : DES                       :
    :                phase 2 key life : 240                       :
    : phase 2 perfect forward secrecy : 1                         :
    :                         created : 2012-03-05T14:07:34-06:00 :
    :                        modified : 2017-05-17T12:01:33-06:00 :
    :.................................:...........................:
    Address Translations:
    :.......:...................:......................:...................:......................:.................:
    :   id  : static IP address : static IP address id : remote IP address : remote IP address id :       note      :
    :.......:...................:......................:...................:......................:.................:
    : 15920 :    10.1.249.86    :       9791681        :    158.85.80.22   :        98828         :  windows server :
    : 15918 :    10.1.249.84    :       9791679        :    158.85.80.20   :        98824         :   unix server   :
    :.......:...................:......................:...................:......................:.................:
    Internal Subnets:
    :........:....................:......:......:
    :   id   : network identifier : cidr : note :
    :........:....................:......:......:
    : 180767 :    10.28.67.128    :  26  :      :
    :........:....................:......:......:
    Remote Subnets:
    :......:....................:......:......:
    :  id  : network identifier : cidr : note :
    :......:....................:......:......:
    : 7852 :    158.85.80.20    :  30  :      :
    :......:....................:......:......:
    Static Subnets:
    :........:....................:......:......:
    :   id   : network identifier : cidr : note :
    :........:....................:......:......:
    : 231807 :    10.1.249.84     :  30  :      :
    :........:....................:......:......:
    Service Subnets:
    :........:....................:......:......:
    :   id   : network identifier : cidr : note :
    :........:....................:......:......:
    : 162079 :     10.0.80.0      :  25  :      :
    :........:....................:......:......:

.. _cli_ipsec_update:

ipsec update
------------
Most values listed in the tunnel context detail printout can be modified using the ``ipsec update`` command. The following is given when executing with the ``-h|--help`` option and highlights all properties that may be modified.
::

    $ slcli ipsec update -h
    Usage: slcli ipsec update [OPTIONS] CONTEXT_ID

      Update tunnel context properties.

      Updates are made atomically, so either all are accepted or none are.

      Key life values must be in the range 120-172800.

      Phase 2 perfect forward secrecy must be in the range 0-1.

      A separate configuration request should be made to realize changes on
      network devices.

    Options:
      --friendly-name TEXT            Friendly name value
      --remote-peer TEXT              Remote peer IP address value
      --preshared-key TEXT            Preshared key value
      --p1-auth, --phase1-auth [MD5|SHA1|SHA256]
                                      Phase 1 authentication value
      --p1-crypto, --phase1-crypto [DES|3DES|AES128|AES192|AES256]
                                      Phase 1 encryption value
      --p1-dh, --phase1-dh [0|1|2|5]  Phase 1 diffie hellman group value
      --p1-key-ttl, --phase1-key-ttl INTEGER RANGE
                                      Phase 1 key life value
      --p2-auth, --phase2-auth [MD5|SHA1|SHA256]
                                      Phase 2 authentication value
      --p2-crypto, --phase2-crypto [DES|3DES|AES128|AES192|AES256]
                                      Phase 2 encryption value
      --p2-dh, --phase2-dh [0|1|2|5]  Phase 2 diffie hellman group value
      --p2-forward-secrecy, --phase2-forward-secrecy INTEGER RANGE
                                      Phase 2 perfect forward secrecy value
      --p2-key-ttl, --phase2-key-ttl INTEGER RANGE
                                      Phase 2 key life value
      -h, --help                      Show this message and exit.

.. _cli_ipsec_configure:

ipsec configure
---------------
A request to configure SoftLayer network devices for a given tunnel context can be issued using the ``ipsec configure`` command.

.. note::

     Once a configuration request is received, the IPSEC tunnel context will be placed into an unmodifiable state, and further changes against the tunnel context will be prevented. Once configuration changes have been made, the tunnel context may again be modified. The unmodifiable state of a tunnel context is indicated by an *advanced configuration flag* value of 1.

.. _cli_ipsec_subnet_add:

ipsec subnet-add
----------------
Internal, remote and service subnets can be associated to an IPSEC tunnel context using the ``ipsec subnet-add`` command. Additionally, remote subnets can be created using this same command, which will then be associated to the targeted tunnel context.

.. note::

    The targeted subnet type must be specified. A subnet id must be provided when associating internal and service subnets. Either a subnet id or a network identifier must be provided when associating remote subnets. If a network identifier is provided when associating a remote subnet, that subnet will first be created and then associated to the tunnel context.

The following is an exmaple of associating an internal subnet to a tunnel context.
::

    $ slcli ipsec subnet-add 445 --subnet-id 180767 --subnet-type internal
    Added internal subnet #180767

The following is an example of creating and associating a remote subnet to a tunnel context.
::

    $ slcli ipsec subnet-add 445 --subnet-type remote --network 50.100.0.0/26
    Created subnet 50.100.0.0/26 #21268
    Added remote subnet #21268

.. _cli_ipsec_subnet_remove:

ipsec subnet-remove
-------------------
Internal, remote and service subnets can be disassociated from an IPSEC tunnel context via the ``ipsec subnet-remove`` command.

.. note::

    The targeted subnet id and type must be specified. When disassociating remote subnets, that subnet record will also be deleted.

The following is an example of disassociating an internal subnet from a tunnel context.
::

    $ slcli ipsec subnet-remove 445 --subnet-id 180767 --subnet-type internal
    Removed internal subnet #180767

.. _cli_ipsec_translation_add:

ipsec translation-add
---------------------
Address translation entries can be added to a tunnel context to provide NAT functionality from a statically routed subnet associated with the tunnel context to a remote subnet. This action is performed with the ``ipsec translation-add`` command.

.. note::

    Both static and remote IP address values must be specified. An optional note value may also be provided.

The following is an example of adding a new address translation entry.
::

    $ slcli ipsec translation-add 445 --static-ip 10.1.249.87 --remote-ip 50.100.0.10 --note 'email server'
    Created translation from 10.1.249.87 to 50.100.0.10 #15922

.. _cli_ipsec_translation_remove:

ipsec translation-remove
------------------------
Address translation entries can be removed using the ``ipsec translation-remove`` command.

The following is an example of removing an address translation entry.
::

    $ slcli ipsec translation-remove 445 --translation-id 15922
    Removed translation #15922

.. _cli_ipsec_translation_update:

ipsec translation-update
------------------------
Address translation entries may also be modified using the ``ipsec translation-update`` command.

The following is an example of updating an existing address translation entry.
::

    $ slcli ipsec translation-update 445 --translation-id 15924 --static-ip 10.1.249.86 --remote-ip 50.100.0.8 --note 'new email server'
    Updated translation #15924
