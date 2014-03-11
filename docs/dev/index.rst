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
Before working with the SoftLayer Python API client source, we strongly recommend that you know how to use Python's virtualization environment, `virtualenv <https://pypi.python.org/pypi/virtualenv>`_. Virtualenv allows you to create Python setups that are individually tailored to particular develpment efforts. Each environment can have its own set of libraries, and even its own Python interpreter; each is isolated from the other environments so the possibilities difficulties arising from library conflicts is reduced.

After you have virtualenv, you should set up a virtual environment and activate it whenever you are working on softlayer-python. The commands needed to setup an environment and activate it might look something like this:

::

  virtualenv --no-site-packages softlayer_env
  
  source softlayer_env/bin/activate

Please refer to the virtualenv documentation for more information about creating, and working with virtual environments.

Once you have an appropriate environment, you will then download the SoftLayer API Python Bindings source code by following the :ref:`installation instructions <install_from_source>`. Change into softlayer-python source directory and run the following to install the pre-requisites needed to run the development tests:

::

  pip install -r tools/test-requirements.txt


Testing
-------
The project have a mix of functional and unit tests. All the tests run using `nose <https://nose.readthedocs.org>`_. Some of the tests make use of the `mock <http://www.voidspace.org.uk/python/mock/>`_ package. To run the test suite, change into the base directory and run:

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
This project follows :pep:`8` and most of the style suggestions that pyflakes recommends. Run `Flake8 <https://pypi.python.org/pypi/flake8/2.0>`_ regularly.


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
