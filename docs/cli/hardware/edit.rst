.. click:: SoftLayer.CLI.hardware.edit:cli
   :prog: hw edit
   :show-nested:

When setting port speed, use "-1" to indicate best possible configuration. Using 10/100/1000/10000 on a server with a redundant interface may result the interface entering a degraded state. See `setPublicNetworkInterfaceSpeed <http://sldn.softlayer.com/reference/services/SoftLayer_Hardware_Server/setPublicNetworkInterfaceSpeed/>`_ for more information.