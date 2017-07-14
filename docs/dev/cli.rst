.. _cli_dev:

Command-Line Interface Developer Guide
======================================

The SoftLayer CLI can be used to manage many different SoftLayer services directly from the command line.

The command line parsing is currently based on `click <http://click.pocoo.org/>`_, which is a command parsing library along with some additions to dynamically load modules from a routes-like file and from `entry points <https://pythonhosted.org/setuptools/setuptools.html#entry-points>`_.

First Example
-------------
For the first example, we can create `slcli table-example` by creating the following file at SoftLayer/CLI/table_example.py:

::

    """A formatting table example."""
    from SoftLayer.CLI import environment
    from SoftLayer.CLI import formatting

    import click


    @click.command()
    @environment.pass_env
    def cli(env):
        """This returns an table that highlights how tables are output"""
        # create a table with two columns: col1, col2
        table = formatting.Table(['col1', 'col2'])

        # align the data facing each other
        # valid values are r, c, l for right, center, left
        # note, these are suggestions based on the format chosen by the user
        table.align['col1'] = 'r'
        table.align['col2'] = 'l'

        # add rows
        table.add_row(['test', 'test'])
        table.add_row(['test2', 'test2'])

        env.fout(table)

Then we need to register it so that `slcli table-example` will know to route to this new module. We do that by adding ALL_ROUTES in SoftLayer/CLI/routes.py to include the following:

::

    ...
    ('table-example', 'SoftLayer.CLI.table_example:cli'),
    ...

Which gives us
::

  $ slcli table-example
  :.......:.......:
  :  col1 : col2  :
  :.......:.......:
  :  test : test  :
  : test2 : test2 :
  :.......:.......:

  $ slcli --format=raw table-example
   test   test
   test2  test2

Formatting of the data represented in the table is actually controlled upstream from the CLIRunnable's making supporting more data formats in the future easier.


Arguments
---------
A command usually isn't very useful without context or arguments of some kind. With click, you have a large array of argument and option types at your disposal. Additionally, with the SoftLayer CLI, we have global options and context which is stored in `SoftLayer.CLI.environment.Environment` and is attainable through a decorator located at `SoftLayer.CLI.environment.pass_env`. An example of options and the environment is shown below. It also shows how output should be done using `env.out` instead of printing. This is used for testing and to have a consistent way to print things onto the screen.

::

    from SoftLayer.CLI import environment

    import click


    @click.command()
    @click.option("--number",
                  required=True,
                  type=click.INT,
                  help="print different output")
    @click.option("--choice",
                  type=click.Choice(['this', 'that']),
                  help="print different output")
    @click.option("--test", help="print different output")
    @environment.pass_env
    def cli(env, number, choice, test):
        """Argument parsing example"""

        if test:
            env.out("Just testing, move along...")
        else:
            env.out("This is fo'realz!")

        if choice == 'this':
            env.out("Selected this")
        elif choice == 'that':
            env.out("Selected that")

        env.out("This is a number: %d" % number)


Refer to the click library documentation for more options.


Accessing the API
-----------------
A SoftLayer client is stood up for every command and is available through `SoftLayer.CLI.environment.Environment.client`. The example below shows how to make a simple API call to the SoftLayer_Account::getObject.

::

    from SoftLayer.CLI import environment

    import click


    @click.command()
    @environment.pass_env
    def cli(env):
        """Using the SoftLayer API client"""

        account = env.client['Account'].getObject()
        return account['companyName']


Aborting execution
------------------

When a confirmation fails, you probably want to stop execution and give a non-zero exit code. To do that, raise a `SoftLayer.CLI.exceptions.CLIAbort` exception with the message for the user as the first parameter. This will prevent any further execution and properly return the right error code.

::

    raise CLIAbort("Aborting. Failed confirmation")
