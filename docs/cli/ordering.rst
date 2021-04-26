.. _cli_order:

Ordering
========
The Order :ref:`cli` commands can be used to build an order for any product in the SoftLayer catalog.

The basic flow for ordering goes something like this...

#. package-list
#. category-list <package key name>
#. item-list <package key name>
#. place <package key name> <item key names> <location>





.. click:: SoftLayer.CLI.order.package_list:cli
    :prog: order package-list
    :show-nested:


.. note::
    * CLOUD_SERVER: These are Virtual Servers
    * BARE_METAL_INSTANCE: Hourly Bare Metal
    * BARE_METAL_SERVER: Other monthly server types
    * `#_PROC_#_DRIVES`: Packages in this format will contain only this CPU model and Drive bays
    * ADDITIONAL_PRODUCTS: Additional IPs, Vlans, SSL certs and other things are in here
    * NETWORK_GATEWAY_APPLIANCE: Vyattas

    Bluemix services listed here may still need to be ordered through the Bluemix CLI/Portal


.. click:: SoftLayer.CLI.order.package_locations:cli
    :prog: order package-locations
    :show-nested:

.. click:: SoftLayer.CLI.order.category_list:cli
    :prog: order category-list
    :show-nested:

Shows all the available categories for a certain package, useful in finding the required categories. Categories that are required will need to have a corresponding item included with any orders

These are all the required categories for ``BARE_METAL_SERVER``
::

    $ slcli order category-list BARE_METAL_SERVER
    :........................................:.......................:............:
    :                  name                  :      categoryCode     : isRequired :
    :........................................:.......................:............:
    :                 Server                 :         server        :     Y      :
    :            Operating System            :           os          :     Y      :
    :                  RAM                   :          ram          :     Y      :
    :            Disk Controller             :    disk_controller    :     Y      :
    :            First Hard Drive            :         disk0         :     Y      :
    :            Public Bandwidth            :       bandwidth       :     Y      :
    :           Uplink Port Speeds           :       port_speed      :     Y      :
    :           Remote Management            :   remote_management   :     Y      :
    :          Primary IP Addresses          :    pri_ip_addresses   :     Y      :
    :    VPN Management - Private Network    :     vpn_management    :     Y      :
    :........................................:.......................:............:

.. click:: SoftLayer.CLI.order.item_list:cli
    :prog: order item-list
    :show-nested:

Shows all the prices for a given package. Collect all the items you want included on your server. Don't forget to include the required category items. If forgotten, ``order place`` will tell you about it.

.. click:: SoftLayer.CLI.order.preset_list:cli
    :prog: order preset-list
    :show-nested:



.. click:: SoftLayer.CLI.order.place:cli
    :prog: order place
    :show-nested:

Now that you have the package you want, the prices needed, and found a location, it is time to place an order.

order place <preset>
^^^^^^^^^^^^^^^^^^^^

::

    $ slcli --really order place --preset D2620V4_64GB_2X1TB_SATA_RAID_1 BARE_METAL_SERVER  TORONTO  \
        OS_UBUNTU_16_04_LTS_XENIAL_XERUS_64_BIT \
        BANDWIDTH_0_GB_2  \
        1_GBPS_PRIVATE_NETWORK_UPLINK  \
        REBOOT_KVM_OVER_IP 1_IP_ADDRESS  \
        UNLIMITED_SSL_VPN_USERS_1_PPTP_VPN_USER_PER_ACCOUNT \
        --extras '{"hardware": [{"hostname" : "testOrder", "domain": "cgallo.com"}]}' \
        --complex-type SoftLayer_Container_Product_Order_Hardware_Server


order place <Virtual Server>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    $ slcli order place --billing hourly CLOUD_SERVER DALLAS13 \
        GUEST_CORES_4 \
        RAM_16_GB \
        REBOOT_REMOTE_CONSOLE \
        1_GBPS_PUBLIC_PRIVATE_NETWORK_UPLINKS \
        BANDWIDTH_0_GB_2 \
        1_IP_ADDRESS \
        GUEST_DISK_100_GB_SAN \
        OS_UBUNTU_16_04_LTS_XENIAL_XERUS_MINIMAL_64_BIT_FOR_VSI \
        MONITORING_HOST_PING \
        NOTIFICATION_EMAIL_AND_TICKET \
        AUTOMATED_NOTIFICATION \
        UNLIMITED_SSL_VPN_USERS_1_PPTP_VPN_USER_PER_ACCOUNT \
        --extras '{"virtualGuests": [{"hostname": "test", "domain": "softlayer.com"}]}' \
        --complex-type SoftLayer_Container_Product_Order_Virtual_Guest



Quotes
======
.. click:: SoftLayer.CLI.order.quote:cli
    :prog: order quote
    :show-nested:


.. click:: SoftLayer.CLI.order.quote_list:cli
    :prog: order quote-list
    :show-nested:

.. click:: SoftLayer.CLI.order.quote_detail:cli
    :prog: order quote-detail
    :show-nested:

.. click:: SoftLayer.CLI.order.quote_save:cli
    :prog: order quote-save
    :show-nested:

.. click:: SoftLayer.CLI.order.place_quote:cli
    :prog: order place-quote
    :show-nested:

Lookup
======
.. click:: SoftLayer.CLI.order.lookup:cli
    :prog: order lookup
    :show-nested:
