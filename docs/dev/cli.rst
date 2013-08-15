.. _cli_dev:

.. note::
  
  Full example module available :ref:`here <example_module>`

Command-Line Interface Developer Guide
======================================

A CLI interface is broken into 4 major parts:

* module
* docblock
* action
* docblock
* docblock


Defining a module
-----------------
A module is a python module residing in `SoftLayer/CLI/modules/<module>.py`.  The filename represented here is what is directly exposed after the `sl` command. I.e. `sl cci` is `SoftLayer/CLI/modules/cci.py`.  The module's docblock is used as the `argument parser <http://docopt.org/>`_ and usage the end user will see.  `SoftLayer.CLI.helpers` contain all the helper functions and classes used for creating a CLI interface.  This is a typical setup and how it maps:

::

  """
  usage: sl example [<command>] [<args>...] [options]

  Example implementation of a CLI module

  Available commands are:
    parse   Parsing args example
    pretty  Formatted print example
    print   Print example
  """

There are some tenants for styling the doc blocks
 * These are parsed with `docopt <http://docopt.org/>`_ so conform to the spec.
 * Two spaces before commands in a command list and options in an option list. 
 * Align the descriptions two spaces after the loggest command/option
 * If a description has to take up more than one line, indent two spaces past the current indention for all additional lines.
 * Alphabetize all commands/option listings. For options, use the long name to judge ordering.


Action
------
Actions are implemented using classes in the module that subclass `SoftLayer.CLI.CLIRunnable`.  The actual class name is irrelevant for the implementation details as it isn't used anywhere.  The docblock is used as the arguement parser as well.  Unlike the modules docblock, additional, common, arguments are added to the end as well; i.e. `--config` and `--format`.

::

  class CLIRunnable(object):
      action = None

      @staticmethod
      def add_additional_args(parser):
          pass

      @staticmethod
      def execute(client, args):
          pass

The required interfaces are:

* The docblock (__doc__) for docopt
* action class attribute
* def execute(client, args)

  - Don't forget the @staticmethod annotation!
  - you can also use @classmethod and use execute(cls, client, args) if you plan on dispatching instead of executing a simple task.

A minimal implementation for `sl example print` would look like this:
::

  class ExampleAction(CLIRunnable):
      """
  usage: sl example print [options]

  Print example
  """

      action = 'print'

      @staticmethod
      def execute(client, args):
          print "EXAMPLE!"


Which in turn, works like this:
::

  $ sl example print
  EXAMPLE!
  $ sl example print -h
  usage: sl example print [options]

  Print example

  Standard Options:
    --format=ARG           Output format. [Options: table, raw] [Default: table]
    -C FILE --config=FILE  Config file location. [Default: ~/.softlayer]
    -h --help              Show this screen

Output
------
The `execute()` method is expected to return either `None` or an instance of `SoftLayer.CLI.helpers.Table`.  When `None` is returned, it assumes all output is handled inside of `execute`.  `SoftLayer.CLI.modules.dns.DumpZone` is a great example of when handling your own output is ideal as the data is already coming back preformatted from  the API.  99% of the time though, data will be raw and unformatted.  As an example, we create `sl example pretty` as such:

::

  class ExamplePretty(CLIRunnable):
      """
  usage: sl example pretty [options]

  Pretty output example
  """

      action = 'pretty'

      @staticmethod
      def execute(client, args):
          # create a table with two columns: col1, col2
          t = Table(['col1', 'col2'])

          # align the data facing each other
          # valid values are r, c, l for right, center, left
          # note, these are suggestions based on the format chosen by the user
          t.align['col1'] = 'r'
          t.align['col2'] = 'l'

          # add rows
          t.add_row(['test', 'test'])
          t.add_row(['test2', 'test2'])

          return t

Which gives us
::

  $ sl example pretty
  :.......:.......:
  :  col1 : col2  :
  :.......:.......:
  :  test : test  :
  : test2 : test2 :
  :.......:.......:

  $ sl example pretty --format raw
   test   test  
   test2  test2 

Formatting of the data represented in the table is actually controlled upstream from the CLIRunnable's making supporting more data formats in the future easier.


Adding arguments
----------------
Refer to docopt for more complete documentation

::

  class ExampleArgs(CLIRunnable):
      """
  usage: sl example parse [--test] [--this=THIS|--that=THAT]
                          (--one|--two) [options]

  Argument parsing example

  Options:
    --test  Print different output
  """

      action = 'parse'

      @staticmethod
      def execute(client, args):
          if args.get('--test'):
              print "Just testing, move along..."
          else:
              print "This is fo'realz!"

          if args['--one']:
              print 1
          elif args['--two']:
              print 2

          if args.get('--this'):
              print "I gots", args['--this']

          if args.get('--that'):
              print "you dont have", args['--that']

Accessing the API
-----------------

API access is available via the first argument of `execute` which will be an initialized copy of `SoftLayer.API.Client`.  Please refer to [using the api](API-Usage) for further details on howto use the `Client` object.

Confirmations
-------------

All confirmations should be easily bypassed by checking for `args['--really']`.  To inject `--really` add `options = ['confirm']` to the class definition, typically just below `action`.  This ensures that `--really` is consistent throughout the CLI.

::

  class ExampleArgs(CLIRunnable):
      """
  usage: sl example parse [--test] [--this=THIS|--that=THAT]
                          (--one|--two) [options]

  Argument parsing example

  Options:
    --test  Print different output
  """

      action = 'parse'
      options = ['confirm']  # confirm adds the '-y|--really' options and help

      @staticmethod
      def execute(client, args):
          pass

There are two primary confirmation prompts that both leverage `SoftLayer.CLI.valid_response`:

* `SoftLayer.CLI.helpers.confirm`
* `SoftLayer.CLI.helpers.no_going_back`

`no_going_back` accepts a single confirmation parameter that is generally unique to that action.  This is similar to typing in the hostname of a machine you are canceling or some other string that isn't reactionary such as "yes", "just do it".  Some good examples would be the ID of the object, a phrase "I know what I am doing" or anything of the like.  It returns True, False, or None.  The prompt string is pre-defined.

`confirm` is a lot more flexible in that you can set the prompt string, allowing default values, and such.  But it's limited to 'yes' or 'no' values.  Returns True, False, or None.

::

  confirmation = args.get('--really') or no_going_back('YES')

  if confirmation:
      pass


Aborting execution
------------------

When a confirmation fails, you will need to bail out of `execute()`.  Raise a `SoftLayer.CLI.helpers.CLIAbort` with the message for the user as the first parameter.  This will prevent any further execution and properly return the right error code.

::

  if not confirmation:
     raise CLIAbort("Aborting. Failed confirmation")
