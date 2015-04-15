.. _example_module:

:orphan:

Example CLI Module
==================

::

    """
    usage: slcli example [<command>] [<args>...] [options]

    Example implementation of a CLI module

    Available commands are:
      parse   parsing args example
      pretty  formatted print example
      print   print example
    """

    from SoftLayer.CLI import (
        CLIRunnable, Table, no_going_back, confirm)


    class ExampleAction(CLIRunnable):
        """
    usage: slcli example print [options]

    Print example
    """

        action = 'print'

        def execute(self, args):
            print "EXAMPLE!"


    class ExamplePretty(CLIRunnable):
        """
    usage: slcli example pretty [options]

    Pretty output example
    """

        action = 'pretty'

        def execute(self, args):
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


    class ExampleArgs(CLIRunnable):
        """
    usage: slcli example parse [--test] [--this=THIS|--that=THAT]
                            (--one|--two) [options]

    Argument parsing example

    Options:
      --test  Print different output
    """

        action = 'parse'
        options = ['confirm']

        def execute(self, args):
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
