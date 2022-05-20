.. _cli_reports:


Reports
========


There are a few report type commands in the SLCLI.

.. click:: SoftLayer.CLI.summary:cli
   :prog: summary
   :show-nested:


A list of datacenters, and how many servers, VSI, vlans, subnets and public_ips are in each.


.. click:: SoftLayer.CLI.report.bandwidth:cli
   :prog: report bandwidth
   :show-nested:



.. click:: SoftLayer.CLI.report.dc_closures:cli
   :prog: report datacenter-closures
   :show-nested:


Displays some basic information about the Servers and other resources that are in Datacenters scheduled to be
decommissioned in the near future.
See `IBM Cloud Datacenter Consolidation <https://cloud.ibm.com/docs/get-support?topic=get-support-dc-closure>`_ for
more information
