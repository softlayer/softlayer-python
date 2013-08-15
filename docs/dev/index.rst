.. _api_dev:

Contribution Guide
==================
This page explains how to get started contributing code to the SoftLayer API Python Bindings project.


Code Organization
-----------------

* **docs** - Where The source to this documentation lives.
* **SoftLayer** - All the source lives under here.

  * **API** - Primary API client.
  * **CLI** - Code for the command-line interface.

    * **modules** - CLI Modules.
  * **managers** - API Managers. Abstractions to help use the API.


Setting Up A Dev Environment
----------------------------
Before installing/downloading anything I highly recommend learning how to use Python's `virtualenv <https://pypi.python.org/pypi/virtualenv>`_. Virtualenv allows you to have isolated python environments, which is extremely useful for development. After you have a virtualenv, download the SoftLayer API Python Bindings source code. That's explained here: :ref:`install`. After you have the source, change into the base directory and run the following to install the pre-requisites for testing the project. Make sure you've activated your virtualenv before you do this.

::

  pip install -r requirements


Testing
-------
The project have a mix of functional and unit tests. All the tests run using `nose <https://nose.readthedocs.org>`_. To run the test suite, change into the base directory and run:

::

  python setup.py nosetests


To test with all supported versions of Python, this project utilizes `tox <https://pypi.python.org/pypi/tox>`_.

To avoid having to install those versions of Python locally, you can also set up `Travis <https://travis-ci.org>`_ on your fork. This can run all the required tests on every code push to github. This is highly recommended.


Documentation
-------------
The project is documented in `reStructuredText <http://sphinx-doc.org/rest.html>`_ and built using `Sphinx <http://sphinx-doc.org/>`_. If you have `fabric <http://fabfile.org>`_ installed, you simply need to run the following to build the docs:

::

  fab make_html

The documentation will be built in `docs/_build/html`. If you don't have fabric, use the following commands.

::

  cd docs
  make html

The primary docs are built at `Read the Docs <https://readthedocs.org/projects/softlayer-api-python-client/>`_.


Style
-----
This project follows :pep:`8` and most of the style suggestions that pyflakes recommends. `Flake8 <https://pypi.python.org/pypi/flake8/2.0>`_ should be ran regularly.


Contributing
------------
Contributing to the Python API bindings follows the fork-pull-request model on `github <http://github.com>`_. The project uses Github's `issues <https://github.com/softlayer/softlayer-api-python-client/issues>`_ and `pull requests <https://github.com/softlayer/softlayer-api-python-client/pulls>`_ to manage source control, bug fixes and new feature development regarding the API bindings and the CLI.


Developer Resources
-------------------
.. toctree::

   SoftLayer API Documentation <http://sldn.softlayer.com/reference/softlayerapi>
   Source on Github <https://github.com/softlayer/softlayer-api-python-client>
   Issues <https://github.com/softlayer/softlayer-api-python-client/issues>
   PyPI <https://pypi.python.org/pypi/softlayer/>
   Twitter <https://twitter.com/SoftLayerDevs>
   #softlayer on freenode <irc://irc.freenode.net/#softlayer>
