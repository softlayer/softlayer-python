.. _vs_reserved_capacity_user_docs:

Working with Reserved Capacity
==============================
There are two main concepts for Reserved Capacity. The `Reserved Capacity Group <https://softlayer.github.io/reference/services/SoftLayer_Virtual_ReservedCapacityGroup/>`_ and the `Reserved Capacity Instance <https://softlayer.github.io/reference/services/SoftLayer_Virtual_ReservedCapacityGroup_Instance/>`_
The Reserved Capacity Group, is a set block of capacity set aside for you at the time of the order. It will contain a set number of Instances which are all the same size. Instances can be ordered like normal VSIs, with the exception that you need to include the reservedCapacityGroupId, and it must be the same size as the group you are ordering the instance in. 

- `About Reserved Capacity <https://console.bluemix.net/docs/vsi/vsi_about_reserved.html>`_
- `Reserved Capacity FAQ <https://console.bluemix.net/docs/docs/vsi/vsi_faqs_reserved.html>`_

The SLCLI supports some basic Reserved Capacity Features.


.. _cli_vs_capacity_create:

vs capacity create
------------------
This command will create a Reserved Capacity Group.  

.. warning::

    **These groups can not be canceled until their contract expires in 1 or 3 years!**

::

    $ slcli vs capacity create --name test-capacity -d dal13 -b 1411193 -c B1_1X2_1_YEAR_TERM -q 10

vs cacpacity create_options
---------------------------
This command will print out the Flavors that can be used to create a Reserved Capacity Group, as well as the backend routers available, as those are needed when creating a new group.

vs capacity create_guest
------------------------
This command will create a virtual server (Reserved Capacity Instance) inside of your Reserved Capacity Group. This command works very similar to the `slcli vs create` command. 

::

    $ slcli vs capacity create-guest --capacity-id 1234 --primary-disk 25 -H ABCD -D test.com -o UBUNTU_LATEST_64  --ipv6 -k test-key --test

vs capacity detail
------------------
This command will print out some basic information about the specified Reserved Capacity Group. 

vs capacity list
-----------------
This command will list out all Reserved Capacity Groups. a **#** symbol represents a filled instance, and a **-** symbol respresents an empty instance

::

    $ slcli vs capacity list
    :............................................................................................................:
    :                                             Reserved Capacity                                              :
    :......:......................:............:......................:..............:...........................:
    :  ID  :         Name         :  Capacity  :        Flavor        :   Location   :          Created          :
    :......:......................:............:......................:..............:...........................:
    : 1234 :    test-capacity     : ####------ : B1.1x2 (1 Year Term) : bcr02a.dal13 : 2018-09-24T16:33:09-06:00 :
    :......:......................:............:......................:..............:...........................: