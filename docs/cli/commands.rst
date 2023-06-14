.. _cli_commands:

Call API
========

This function allows you to easily call any API. The format is

`slcli call-api SoftLayer_Service method param1 param2 --id=1234 --mask="mask[id,name]"`

Parameters should be in the order they are presented on sldn.softlayer.com. 
Any complex parameters (those that link to other datatypes) should be presented as JSON strings. They need to be enclosed in single quotes (`'`), and variables and strings enclosed in double quotes (`"`).

For example: `{"hostname":"test",ssh_keys:[{"id":1234}]}`

.. click:: SoftLayer.CLI.call_api:cli
    :prog: call-api
    :show-nested:


Shell
=====

.. click:: SoftLayer.shell.core:cli
    :prog: shell
    :show-nested:



MetaData
========

Used to retrieve information about the server making the API call.
Can be called with an un-authenticated API call.

.. click:: SoftLayer.CLI.metadata:cli
    :prog: metadata
    :show-nested:

Search
======

Is an API service that lets you make complex queries about data indexed by the service.
Can be called with an un-authenticated API call.

.. click:: SoftLayer.CLI.search:cli
    :prog: search
    :show-nested:
