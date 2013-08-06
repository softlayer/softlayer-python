.. _config_file:

CLI Configuration File
======================
The CLI loads your settings from a number of different locations.

* Enviorment variables (SL_USERNAME, SL_API_KEY)
* Config file (~/.softlayer)
* Or argument (-C/path/to/config or --config=/path/to/config)

The configuration file is INI-based and requires the `softlayer` section to be present. The only required fields are `username` and `api_key`. You can optionally supply the `endpoint_url` as well. This file is created automatically by the `sl config setup` command detailed here: :ref:`config_setup`.

*Full config*
::

  [softlayer]
  username = username
  api_key = oyVmeipYQCNrjVS4rF9bHWV7D75S6pa1fghFl384v7mwRCbHTfuJ8qRORIqoVnha
  endpoint_url = https://api.softlayer.com/xmlrpc/v3/
