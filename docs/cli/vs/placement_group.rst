.. _vs_placement_group_user_docs:

Working with Placement Groups
=============================
A `Placement Group <https://cloud.ibm.com/docs/vsi/vsi_placegroup.html#placement-groups>`_  is a way to control which physical servers your virtual servers get provisioned onto. 

To create a  `Virtual_PlacementGroup <https://softlayer.github.io/reference/services/SoftLayer_Virtual_PlacementGroup/>`_ object, you will need to know the following:

- backendRouterId,  from `getAvailableRouters <https://softlayer.github.io/reference/services/SoftLayer_Virtual_PlacementGroup/getAvailableRouters>`_)
- ruleId, from `getAllObjects <https://softlayer.github.io/reference/services/SoftLayer_Virtual_PlacementGroup_Rule/getAllObjects/>`_
- name, can be any string, but most be unique on your account

Once a placement group is created, you can create new virtual servers in that group. Existing VSIs cannot be moved into a placement group. When ordering a VSI in a placement group, make sure to set the `placementGroupId <https://softlayer.github.io/reference/datatypes/SoftLayer_Virtual_Guest/#placementGroupId>`_ for each guest in your order. 

use the --placementGroup option with `vs create` to specify creating a VSI in a specific group.

::

    
    $ slcli  vs create -H testGroup001 -D test.com -f  B1_1X2X25 -d mex01 -o DEBIAN_LATEST --placementGroup testGroup

Placement groups can only be deleted once all the virtual guests in the group have been reclaimed.

.. _cli_vs_placementgroup_create:

vs placementgroup create
------------------------
This command will create a placement group

::

    $ slcli vs placementgroup create --name testGroup -b bcr02a.dal06 -r SPREAD

Options
^^^^^^^
--name TEXT                     Name for this new placement group.  [required]
-b, --backend_router            backendRouter, can be either the hostname or id.  [required]
-h, --help                      Show this message and exit.



.. _cli_vs_placementgroup_create_options:

vs placementgroup create-options
--------------------------------
This command will print out the available routers and rule sets for use in creating a placement group.

::

    $ slcli vs placementgroup create-options

.. _cli_vs_placementgroup_delete:

vs placementgroup delete
------------------------
This command will remove a placement group. The placement group needs to be empty for this command to succeed.

Options
^^^^^^^
--purge     Delete all guests in this placement group. The group itself can be deleted once all VMs are fully reclaimed

::

    $ slcli vs placementgroup delete testGroup

You can use the flag --purge to auto-cancel all VSIs in a placement group. You will still need to wait for them to be reclaimed before proceeding to delete the group itself.

::

    $ slcli vs placementgroup testGroup --purge


.. _cli_vs_placementgroup_list:

vs placementgroup list
----------------------
This command will list all placement groups on your account. 

::

    $ slcli vs placementgroup list
    :..........................................................................................:
    :                                     Placement Groups                                     :
    :.......:...................:................:........:........:...........................:
    :   Id  :        Name       : Backend Router :  Rule  : Guests :          Created          :
    :.......:...................:................:........:........:...........................:
    : 31741 :       fotest      :  bcr01a.tor01  : SPREAD :   1    : 2018-11-22T14:36:10-06:00 :
    : 64535 :     testGroup     :  bcr01a.mex01  : SPREAD :   3    : 2019-01-17T14:36:42-06:00 :
    :.......:...................:................:........:........:...........................:

.. _cli_vs_placementgroup_detail:

vs placementgroup detail
------------------------
This command will provide some detailed information about a specific placement group

::

    $ slcli vs placementgroup detail testGroup
    :.......:............:................:........:...........................:
    :   Id  :     Name   : Backend Router :  Rule  :          Created          :
    :.......:............:................:........:...........................:
    : 64535 : testGroup  :  bcr01a.mex01  : SPREAD : 2019-01-17T14:36:42-06:00 :
    :.......:............:................:........:...........................:
    :..........:........................:...............:..............:.....:........:...........................:.............:
    :    Id    :           FQDN         :   Primary IP  :  Backend IP  : CPU : Memory :        Provisioned        : Transaction :
    :..........:........................:...............:..............:.....:........:...........................:.............:
    : 69134895 : testGroup62.test.com   : 169.57.70.166 : 10.131.11.32 :  1  :  1024  : 2019-01-17T17:44:50-06:00 :      -      :
    : 69134901 : testGroup72.test.com   : 169.57.70.184 : 10.131.11.59 :  1  :  1024  : 2019-01-17T17:44:53-06:00 :      -      :
    : 69134887 : testGroup52.test.com   : 169.57.70.187 : 10.131.11.25 :  1  :  1024  : 2019-01-17T17:44:43-06:00 :      -      :
    :..........:........................:...............:..............:.....:........:...........................:.............: