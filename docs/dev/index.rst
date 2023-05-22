.. _api_dev:

Contribution Guide
==================
This page explains how to get started contributing code to the SoftLayer API
Python Bindings project.


Code Organization
-----------------


.. image:: /images/SoftLayer-Python.png
  :width: 800
  :alt: SoftLayer-Python Architecture Diagram


Setting Up A Dev Environment
----------------------------
Before working with the SoftLayer Python API client source, we strongly
recommend that you know how to use Python's virtual environment,
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
mistakes in the code using `Flake8 <https://pypi.python.org/pypi/flake8/2.0>`_ and `pylint <https://www.pylint.org/>`_.
You should eliminate the linting errors that are reported before submitting
your code. You can run only the linting checks by using this command:

::

  tox -eanalysis

The project's configuration instructs tox to test against many different
versions of Python. A tox test will use as many of those as it can find on your
local computer.

Using tox to run tests in multiple environments can be very time
consuming. If you wish to quickly run the tests in your own environment, you
may do so using `py.test <http://pytest.org/>`_.  The command to do that
is:

::

  py.test tests


Fixtures
~~~~~~~~

Testing of this project relies quite heavily on fixtures to simulate API calls. When running the unit tests, we use the FixtureTransport class, which instead of making actual API calls, loads data from `/fixtures/SoftLayer_Service_Name.py` and tries to find a variable that matches the method you are calling.

When adding new Fixtures you should try to sanitize the data of any account identifiying results, such as account ids, username, and that sort of thing. It is ok to leave the id in place for things like datacenter ids, price ids. 

To Overwrite a fixture, you can use a mock object to do so. Like either of these two methods:

::

    # From tests/CLI/modules/vs_capacity_tests.py
    from SoftLayer.fixtures import SoftLayer_Product_Package

    def test_create_test(self):
        item_mock = self.set_mock('SoftLayer_Product_Package', 'getItems')
        item_mock.return_value = SoftLayer_Product_Package.getItems_RESERVED_CAPACITY

    def test_detail_pending(self):
        capacity_mock = self.set_mock('SoftLayer_Virtual_ReservedCapacityGroup', 'getObject')
        get_object = {
            'name': 'test-capacity',
            'instances': []
        }
        capacity_mock.return_value = get_object


Documentation
-------------
The project is documented in
`reStructuredText <http://sphinx-doc.org/rest.html>`_ and built using
`Sphinx <http://sphinx-doc.org/>`_. 

For testing locally you can run the following command to build the HTML for this project

::

  cd docs
  sphinx-build -b html ./  ./html

The primary docs are built at
`Read the Docs <http://softlayer-python.readthedocs.org/>`_.

`Recent build output for reference <https://readthedocs.org/projects/softlayer-python/builds/20780252/>`_

::

  git clone --no-single-branch --depth 50 https://github.com/softlayer/softlayer-python.git .
  git checkout --force origin/master
  git clean -d -f -f
  python3.7 -mvirtualenv $READTHEDOCS_VIRTUALENV_PATH
  python -m pip install --upgrade --no-cache-dir pip setuptools
  python -m pip install --upgrade --no-cache-dir pillow==5.4.1 mock==1.0.1 alabaster>=0.7,<0.8,!=0.7.5 commonmark==0.9.1 recommonmark==0.5.0 sphinx<2 sphinx-rtd-theme<0.5 readthedocs-sphinx-ext<2.3 jinja2<3.1.0
  python -m pip install --exists-action=w --no-cache-dir -r docs/requirements.txt
  cat docs/conf.py
  python -m sphinx -T -E -b dirhtml -d _build/doctrees -D language=en . $READTHEDOCS_OUTPUT/html
  python -m sphinx -T -E -b readthedocssinglehtmllocalmedia -d _build/doctrees -D language=en . $READTHEDOCS_OUTPUT/htmlzip
  python -m sphinx -T -E -b latex -d _build/doctrees -D language=en . $READTHEDOCS_OUTPUT/pdf
  cat latexmkrc
  latexmk -r latexmkrc -pdf -f -dvi- -ps- -jobname=softlayer-python -interaction=nonstopmode
  python -m sphinx -T -E -b epub -d _build/doctrees -D language=en . $READTHEDOCS_OUTPUT/epub


Style
-----
This project tries to follow :pep:`8` and most of the style suggestions that pyflakes
recommends. Run `Flake8 <https://pypi.python.org/pypi/flake8/2.0>`_ regularly.
Flake8, with project-specific exceptions, can be run by using tox:

::

  tox -e analysis

Autopep8 can fix a lot of the simple flake8 errors about whitespace and indention. 

::

  autopep8 -r  -a -v -i --max-line-length 119







Contributing
------------
Contributing to the Python API bindings follows the `fork-pull-request model <https://guides.github.com/introduction/flow/>`_ on
`GitHub <http://github.com>`_. The project uses GitHub's
`issue tracker <https://github.com/softlayer/softlayer-python/issues>`_ and
`pull requests <https://github.com/softlayer/softlayer-python/pulls>`_ to
manage source control, bug fixes and new feature development regarding the API
bindings and the CLI. In order to contribute, we require that you sign a contributer agreemenet:

* Sign our contributor agreement (CLA) You can find the :download:`CLA here <cla-individual.md>`.
* If you're contributing on behalf of your employer we'll need a signed copy of our corporate contributor agreement (CCLA) as well.  You can find the :download:`CCLA here <cla-corporate.md>`.


Developer Resources
-------------------
.. toctree::

   SoftLayer API Documentation <https://sldn.softlayer.com/reference/softlayerapi/>
   Source on GitHub <https://github.com/softlayer/softlayer-python>
   Issues <https://github.com/softlayer/softlayer-python/issues>
   Pull Requests <https://github.com/softlayer/softlayer-python/pulls>
   PyPI <https://pypi.python.org/pypi/softlayer/>
   #softlayer on freenode <irc://irc.freenode.net/#softlayer>
