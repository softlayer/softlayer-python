.. _cli_hardware:

Interacting with Hardware
==============================


.. click:: SoftLayer.CLI.hardware.cancel_reasons:cli
   :prog: hw cancel-reasons
   :show-nested:

.. click:: SoftLayer.CLI.hardware.cancel:cli
   :prog: hw cancel
   :show-nested:

.. click:: SoftLayer.CLI.hardware.create_options:cli
   :prog: hw create-options
   :show-nested:

.. click:: SoftLayer.CLI.hardware.create:cli
   :prog: hw create
   :show-nested:


Provides some basic functionality to order a server. `slcli order` has a more full featured method of ordering servers. This command only supports the FAST_PROVISION type.

.. click:: SoftLayer.CLI.hardware.credentials:cli
   :prog: hw credentials
   :show-nested:


.. click:: SoftLayer.CLI.hardware.detail:cli
   :prog: hw detail
   :show-nested:


.. click:: SoftLayer.CLI.hardware.edit:cli
   :prog: hw edit
   :show-nested:

When setting port speed, use "-1" to indicate best possible configuration. Using 10/100/1000/10000 on a server with a redundant interface may result the interface entering a degraded state. See `setPublicNetworkInterfaceSpeed <http://sldn.softlayer.com/reference/services/SoftLayer_Hardware_Server/setPublicNetworkInterfaceSpeed/>`_ for more information.


.. click:: SoftLayer.CLI.hardware.list:cli
   :prog: hw list
   :show-nested:

.. click:: SoftLayer.CLI.hardware.power:power_cycle
   :prog: hw power-cycle
   :show-nested:

.. click:: SoftLayer.CLI.hardware.power:power_off
   :prog: hw power-off
   :show-nested:

.. click:: SoftLayer.CLI.hardware.power:power_on
   :prog: hw power-on
   :show-nested:

.. click:: SoftLayer.CLI.hardware.power:reboot
   :prog: hw reboot
   :show-nested:

.. click:: SoftLayer.CLI.hardware.reload:cli
   :prog: hw reload
   :show-nested:

.. click:: SoftLayer.CLI.hardware.power:rescue
   :prog: hw rescue

.. click:: SoftLayer.CLI.hardware.reflash_firmware:cli
   :prog: hw reflash-firmware
   :show-nested:


Reflash here means the current version of the firmware running on your server will be re-flashed onto the selected hardware. This does require a reboot. See `slcli hw update-firmware` if you want the newest version.

.. click:: SoftLayer.CLI.hardware.update_firmware:cli
   :prog: hw update-firmware
   :show-nested:


This function updates the firmware of a server. If already at the latest version, no software is installed. 

.. click:: SoftLayer.CLI.hardware.toggle_ipmi:cli
   :prog: hw toggle-ipmi
   :show-nested:


   :show-nested:


.. click:: SoftLayer.CLI.hardware.ready:cli
   :prog: hw ready
   :show-nested:

