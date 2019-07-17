.. _cli_event_log:

Event-Log Commands
====================


.. click:: SoftLayer.CLI.event_log.get:cli
    :prog: event-log get
    :show-nested:

There are usually quite a few events on an account, so be careful when using the `--limit -1` option. The command will automatically break requests out into smaller sub-requests, but this command may take a very long time to complete. It will however print out data as it comes in.

.. click:: SoftLayer.CLI.event_log.types:cli
    :prog: event-log types
    :show-nested:


Currently the types are as follows, more may be added in the future.
::
    
    :......................:
    :        types         :
    :......................:
    :       Account        :
    :         CDN          :
    :         User         :
    : Bare Metal Instance  :
    :  API Authentication  :
    :        Server        :
    :         CCI          :
    :        Image         :
    :      Bluemix LB      :
    :       Facility       :
    : Cloud Object Storage :
    :    Security Group    :
    :......................: