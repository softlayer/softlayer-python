"""
    SoftLayer.CLI.exceptions
    ~~~~~~~~~~~~~~~~~~~~~~~~
    Exceptions to be used in the CLI modules.

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: MIT, see LICENSE for more details.
"""


class CLIHalt(SystemExit):
    def __init__(self, code=0, *args):
        super(CLIHalt, self).__init__(*args)
        self.code = code


class CLIAbort(CLIHalt):
    def __init__(self, msg, *args):
        super(CLIAbort, self).__init__(code=2, *args)
        self.message = msg


class ArgumentError(CLIAbort):
    def __init__(self, msg, *args):
        super(ArgumentError, self).__init__(msg, *args)
        self.message = "Argument Error: %s" % msg
