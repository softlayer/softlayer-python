.. _cli_tickets:

Support Tickets
=================

The SoftLayer ticket API is used to create "classic" or Infrastructure Support cases. These tickets will still show up in your web portal, but for the more unified case management API, see the `Case Management API <https://cloud.ibm.com/apidocs/case-management#introduction>`_

.. note::

    Windows Git-Bash users might run into issues with `ticket create` and `ticket update` if --body isn't used, as it doesn't report that it is a real TTY to python, so the default editor can not be launched.


.. click:: SoftLayer.CLI.ticket.create:cli
    :prog: ticket create
    :show-nested:

.. click:: SoftLayer.CLI.ticket.detail:cli
    :prog: ticket detail
    :show-nested:

.. click:: SoftLayer.CLI.ticket.list:cli
    :prog: ticket list
    :show-nested:

.. click:: SoftLayer.CLI.ticket.update:cli
    :prog: ticket update
    :show-nested:

.. click:: SoftLayer.CLI.ticket.upload:cli
    :prog: ticket upload
    :show-nested:

.. click:: SoftLayer.CLI.ticket.subjects:cli
    :prog: ticket subjects
    :show-nested:

.. click:: SoftLayer.CLI.ticket.summary:cli
    :prog: ticket summary
    :show-nested:

.. click:: SoftLayer.CLI.ticket.attach:cli
    :prog: ticket attach
    :show-nested:

.. click:: SoftLayer.CLI.ticket.detach:cli
    :prog: ticket detach
    :show-nested:
