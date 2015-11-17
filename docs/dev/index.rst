.. _api_dev:

Contribution Guide
==================
This page explains how to get started contributing code to the SoftLayer API
Python Bindings project.


Code Organization
-----------------

* **docs** - Where The source to this documentation lives.
* **SoftLayer** - All the source lives under here.

  * **API** - Primary API client.
  * **CLI** - Code for the command-line interface.
  * **managers** - API Managers. Abstractions to help use the API.


Setting Up A Dev Environment
----------------------------
Before working with the SoftLayer Python API client source, we strongly
recommend that you know how to use Python's virtualization environment,
`virtualenv <https://pypi.python.org/pypi/virtualenv>`_. Virtualenv allows you
to create isolated Python environments that are individually tailored to
particular development projects. Each environment can have its own set of
libraries and even its own Python interpreter. This keeps them fully isolated,
reducing the possibility of library conflicts between different projects.

After you have virtualenv, you should set up a virtual environment and activate
it whenever you are working on softlayer-python. The commands needed to setup
an environment and activate it might look something like this:

::

  virtualenv --no-site-packages softlayer_env
  source softlayer_env/bin/activate

Please refer to the virtualenv documentation for more information about
creating, and working with virtual environments.

Once you have an appropriate environment, you will then download the SoftLayer
API Python Bindings source code by following the
:ref:`installation instructions <install_from_source>`. Change into
softlayer-python source directory and run the following to install the
pre-requisites that you'll need in order to run the test suites:

::

  pip install -r tools/test-requirements.txt


Testing
-------
The project has a mix of functional and unit tests. Before submitting changes
to be integrated into the project, you should validate your code using
`tox <https://pypi.python.org/pypi/tox>`_. Simply issue the tox command from
the root of the source tree:

::

  tox

In addition to testing different versions of Python, tox checks for common
mistakes in the code using `Flake8 <https://pypi.python.org/pypi/flake8/2.0>`_.
You should eliminate the simple errors reported by Flake8 before submitting
your code.

The project's configuration instructs tox to test against many different
versions of Python. A tox test will use as many of those as it can find on your
local computer. Rather than installing all those versions, we recommend that
you point the `Travis <https://travis-ci.org>`_ continuous integration tool at
your GitHub fork. Travis will run the test against the full suite of Python
versions every time you push new code.

Using tox to running the tests in multiple environments can be very time
consuming. If you wish to quickly run the tests in your own environment, you
may do so using `py.test <http://pytest.org/>`_.  The command to do that
is:

::

  py.test tests


Documentation
-------------
The project is documented in
`reStructuredText <http://sphinx-doc.org/rest.html>`_ and built using
`Sphinx <http://sphinx-doc.org/>`_. If you have
`fabric <http://fabfile.org>`_ installed, you simply need to run the following
to build the docs:

::

  fab make_html

The documentation will be built in `docs/_build/html`. If you don't have
fabric, use the following commands.

::

  cd docs
  make html

The primary docs are built at
`Read the Docs <http://softlayer-python.readthedocs.org/>`_.


Style
-----
This project follows :pep:`8` and most of the style suggestions that pyflakes
recommends. Run `Flake8 <https://pypi.python.org/pypi/flake8/2.0>`_ regularly.
Flake8, with project-specific exceptions, can be run by using tox:

::

  tox -e analysis


Contributing
------------
Contributing to the Python API bindings follows the fork-pull-request model on
`GitHub <http://github.com>`_. The project uses GitHub's
`issue tracker <https://github.com/softlayer/softlayer-python/issues>`_ and
`pull requests <https://github.com/softlayer/softlayer-python/pulls>`_ to
manage source control, bug fixes and new feature development regarding the API
bindings and the CLI.


Developer Resources
-------------------
.. toctree::

   SoftLayer API Documentation <http://developer.softlayer.com/reference/softlayerapi>
   Source on GitHub <https://github.com/softlayer/softlayer-python>
   Issues <https://github.com/softlayer/softlayer-python/issues>
   Pull Requests <https://github.com/softlayer/softlayer-python/pulls>
   PyPI <https://pypi.python.org/pypi/softlayer/>
   Twitter <https://twitter.com/SoftLayerDevs>
   #softlayer on freenode <irc://irc.freenode.net/#softlayer>
