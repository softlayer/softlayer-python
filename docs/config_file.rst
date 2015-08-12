.. _config_file:


Configuration File
==================
The SoftLayer API bindings load your settings from a number of different
locations.

* Input directly into SoftLayer.create_client_from_env(...)
* Enviorment variables (`SL_USERNAME`, `SL_API_KEY`)
* Config file locations (`~/.softlayer`, `/etc/softlayer.conf`)
* Or argument (`-C/path/to/config` or `--config=/path/to/config`)

The configuration file is INI-based and requires the `softlayer` section to be
present. The only required fields are `username` and `api_key`. You can
optionally supply the `endpoint_url` as well. This file is created
automatically by the `slcli setup` command detailed here:
:ref:`config_setup`.

*Config Example*
::

  [softlayer]
  username = username
  api_key = oyVmeipYQCNrjVS4rF9bHWV7D75S6pa1fghFl384v7mwRCbHTfuJ8qRORIqoVnha
  endpoint_url = https://api.softlayer.com/xmlrpc/v3/
  timeout = 40
