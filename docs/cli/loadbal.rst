.. _cli_loadbalancer:

LoadBalancers
===================================
These commands were added in version `5.8.0 <https://github.com/softlayer/softlayer-python/releases/tag/v5.8.0>`_

LBaaS Commands
~~~~~~~~~~~~~~

- `LBaaS Product <https://www.ibm.com/cloud/load-balancer>`_
- `LBaaS Documentation <https://cloud.ibm.com/docs/infrastructure/loadbalancer-service>`_

.. click:: SoftLayer.CLI.loadbal.detail:cli
   :prog: loadbal detail
   :show-nested:
.. click:: SoftLayer.CLI.loadbal.list:cli
   :prog: loadbal list
   :show-nested:
.. click:: SoftLayer.CLI.loadbal.health:cli
   :prog: loadbal health
   :show-nested:
.. click:: SoftLayer.CLI.loadbal.members:add
   :prog: loadbal member-add
   :show-nested:
.. click:: SoftLayer.CLI.loadbal.members:remove
   :prog: loadbal member-remove
   :show-nested:
.. click:: SoftLayer.CLI.loadbal.pools:add
   :prog: loadbal pool-add
   :show-nested:
.. click:: SoftLayer.CLI.loadbal.pools:edit
   :prog: loadbal pool-edit
   :show-nested:
.. click:: SoftLayer.CLI.loadbal.pools:delete
   :prog: loadbal pool-delete
   :show-nested:
.. click:: SoftLayer.CLI.loadbal.pools:l7pool_add
   :prog: loadbal l7pool-add
   :show-nested:
.. click:: SoftLayer.CLI.loadbal.pools:l7pool_del
   :prog: loadbal l7pool-del
   :show-nested:
.. click:: SoftLayer.CLI.loadbal.order:order
   :prog: loadbal order
   :show-nested:
.. click:: SoftLayer.CLI.loadbal.order:order_options
   :prog: loadbal order-options
   :show-nested:
.. click:: SoftLayer.CLI.loadbal.order:cancel
   :prog: loadbal cancel
   :show-nested:


NetScaler Commands
~~~~~~~~~~~~~~~~~~

.. click:: SoftLayer.CLI.loadbal.ns_detail:cli
   :prog: loadbal ns-detail
   :show-nested:
.. click:: SoftLayer.CLI.loadbal.ns_list:cli
   :prog: loadbal ns-list
   :show-nested: