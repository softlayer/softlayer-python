.. _cli_registration:

Regional Internet Registry(RIR) Commands
========================================

These commands have similar functionality to `RIR Registration <https://cloud.ibm.com/classic/network/rir>`_ page in the portal.

They allow you to configure a Person/Contact that can be used to configure the WHOIS information for a specific subnet. Each account has a default Person/Contact that gets applied when subnets are ordered initially, but if you ever need to configure this, these commands can help.


.. click:: SoftLayer.CLI.registration.detail:cli
    :prog: registration detail
    :show-nested:

.. click:: SoftLayer.CLI.registration.show:cli
    :prog: registration show
    :show-nested:

.. click:: SoftLayer.CLI.registration.person_edit:cli
    :prog: registration person-edit
    :show-nested:

.. click:: SoftLayer.CLI.registration.contacts:cli
    :prog: registration contacts
    :show-nested:

.. click:: SoftLayer.CLI.registration.person_detail:cli
    :prog: registration person-detail
    :show-nested:


.. click:: SoftLayer.CLI.registration.subnet_detail:cli
    :prog: registration subnet-detail
    :show-nested: