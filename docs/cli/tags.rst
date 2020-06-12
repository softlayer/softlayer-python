.. _cli_tags:

Tag Commands
============

These commands will allow you to interact with the **IMS** provier tagging service. The `IBM Global Search and Tagging API <https://cloud.ibm.com/apidocs/tagging#related-apis>`_  can be used to interact with both the **GHOST** provider and **IMS** provider. The **GHOST** provider will handle tags for things outside of the Classic Infrastructure (aka SoftLayer) space.

.. click:: SoftLayer.CLI.tags.list:cli
    :prog: tags list
    :show-nested:

.. click:: SoftLayer.CLI.tags.set:cli
    :prog: tags set
    :show-nested:

.. click:: SoftLayer.CLI.tags.details:cli
    :prog: tags details
    :show-nested:

.. click:: SoftLayer.CLI.tags.delete:cli
    :prog: tags delete
    :show-nested:

.. click:: SoftLayer.CLI.tags.taggable:cli
    :prog: tags taggable
    :show-nested:

.. click:: SoftLayer.CLI.tags.cleanup:cli
    :prog: tags cleanup
    :show-nested:
