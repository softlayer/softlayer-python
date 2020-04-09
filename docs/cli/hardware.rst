.. _cli_hardware:

Interacting with Hardware
==============================


.. click:: SoftLayer.CLI.hardware.bandwidth:cli
   :prog: hardware bandwidth
   :show-nested:

.. click:: SoftLayer.CLI.hardware.cancel_reasons:cli
   :prog: hardware cancel-reasons
   :show-nested:

.. click:: SoftLayer.CLI.hardware.cancel:cli
   :prog: hardware cancel
   :show-nested:

.. click:: SoftLayer.CLI.hardware.create_options:cli
   :prog: hardware create-options
   :show-nested:

.. click:: SoftLayer.CLI.hardware.create:cli
   :prog: hardware create
   :show-nested:


Provides some basic functionality to order a server. `slcli order` has a more full featured method of ordering servers. This command only supports the FAST_PROVISION type.

.. click:: SoftLayer.CLI.hardware.credentials:cli
   :prog: hardware credentials
   :show-nested:


.. click:: SoftLayer.CLI.hardware.detail:cli
   :prog: hardware detail
   :show-nested:

.. click:: SoftLayer.CLI.hardware.billing:cli
   :prog: hw billing
   :show-nested:


.. click:: SoftLayer.CLI.hardware.edit:cli
   :prog: hardware edit
   :show-nested:

**Note :** Using multiple ' **:** ' can cause an error.

     $ slcli hw edit 123456 --tag "cloud:service:db2whoc, cloud:svcplan:flex, cloud:svcenv:prod, cloud:bmixenv:fra"

         TransportError(0): ('Connection aborted.',

         RemoteDisconnected('Remote end closed connection without response',))


When setting port speed, use "-1" to indicate best possible configuration. Using 10/100/1000/10000 on a server with a redundant interface may result the interface entering a degraded state. See `setPublicNetworkInterfaceSpeed <http://sldn.softlayer.com/reference/services/SoftLayer_Hardware_Server/setPublicNetworkInterfaceSpeed/>`_ for more information.

.. click:: SoftLayer.CLI.hardware.list:cli
   :prog: hardware list
   :show-nested:

.. click:: SoftLayer.CLI.hardware.power:power_cycle
   :prog: hardware power-cycle
   :show-nested:

.. click:: SoftLayer.CLI.hardware.power:power_off
   :prog: hardware power-off
   :show-nested:

.. click:: SoftLayer.CLI.hardware.power:power_on
   :prog: hardware power-on
   :show-nested:

.. click:: SoftLayer.CLI.hardware.power:reboot
   :prog: hardware reboot
   :show-nested:

.. click:: SoftLayer.CLI.hardware.reload:cli
   :prog: hardware reload
   :show-nested:

.. click:: SoftLayer.CLI.hardware.power:rescue
   :prog: hardware rescue

.. click:: SoftLayer.CLI.hardware.reflash_firmware:cli
   :prog: hardware reflash-firmware
   :show-nested:


Reflash here means the current version of the firmware running on your server will be re-flashed onto the selected hardware. This does require a reboot. See `slcli hw update-firmware` if you want the newest version.

.. click:: SoftLayer.CLI.hardware.update_firmware:cli
   :prog: hardware update-firmware
   :show-nested:


This function updates the firmware of a server. If already at the latest version, no software is installed. 

.. click:: SoftLayer.CLI.hardware.toggle_ipmi:cli
   :prog: hardware toggle-ipmi
   :show-nested:


.. click:: SoftLayer.CLI.hardware.ready:cli
   :prog: hardware ready
   :show-nested:

.. click:: SoftLayer.CLI.hardware.dns:cli
   :prog: hardware dns-sync
   :show-nested:

.. click:: SoftLayer.CLI.hardware.storage:cli
   :prog: hw storage
   :show-nested:
