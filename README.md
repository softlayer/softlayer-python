SoftLayer API Python Client
===========================
SoftLayer API bindings for Python. For use with 
[SoftLayer's API](http://sldn.softlayer.com/reference/softlayerapi). For more 
documentation, [go here](http://softlayer.github.com/softlayer-api-python-client/).

This library provides a simple interface to interact with SoftLayer's XML-RPC
API and provides support for many of SoftLayer API's features like
[object masks](http://sldn.softlayer.com/article/Using-Object-Masks-SoftLayerAPI). 
It also contains a command-line interface that can be used to access various 
SoftLayer services using the API.

Installation
------------
Install via pip:
```
pip install softlayer
```

Or you can install from source. Download source and run:

```
python setup.py install
```


The most up to date version of this library can be found on the SoftLayer
GitHub public repositories: http://github.com/softlayer. Please post to the
SoftLayer forums http://forums.softlayer.com/ or open a support ticket in the
SoftLayer customer portal if you have any questions regarding use of this
library.

System Requirements
-------------------
* This library has been tested on Python 2.5, 2.6, 2.7, 3.2 and 3.3.
* A valid SoftLayer API username and key are required to call SoftLayer's API
* A connection to SoftLayer's private network is required to connect to
  SoftLayer’s private network API endpoints.


Copyright
---------
This software is Copyright (c) 2013 [SoftLayer Technologies, Inc](http://www.softlayer.com/).
See the bundled LICENSE file for more information.
