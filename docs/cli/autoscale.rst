.. _cli_autoscale:

Autoscale Commands
==================
These commands were added in version `5.8.1 <https://github.com/softlayer/softlayer-python/releases/tag/v5.8.1>`_

For making changes to the triggers or the autoscale group itself, see the `Autoscale Portal`_

- `Autoscale Product <https://www.ibm.com/cloud/auto-scaling>`_
- `Autoscale Documentation <https://cloud.ibm.com/docs/vsi?topic=virtual-servers-about-auto-scale>`_
- `Autoscale Portal`_

.. click:: SoftLayer.CLI.autoscale.list:cli
    :prog: autoscale list
    :show-nested:

.. click:: SoftLayer.CLI.autoscale.detail:cli
    :prog: autoscale detail
    :show-nested:

.. click:: SoftLayer.CLI.autoscale.scale:cli
    :prog: autoscale scale
    :show-nested:

.. click:: SoftLayer.CLI.autoscale.logs:cli
    :prog: autoscale logs
    :show-nested:

.. click:: SoftLayer.CLI.autoscale.tag:cli
    :prog: autoscale tag
    :show-nested:

.. click:: SoftLayer.CLI.autoscale.edit:cli
    :prog: autoscale edit
    :show-nested:

.. click:: SoftLayer.CLI.autoscale.delete:cli
    :prog: autoscale delete
    :show-nested:

.. click:: SoftLayer.CLI.autoscale.create:cli
    :prog: autoscale create
    :show-nested:


.. _Autoscale Portal: https://cloud.ibm.com/classic/autoscale