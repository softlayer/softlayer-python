"""
    SoftLayer.CLI.exceptions
    ~~~~~~~~~~~~~~~~~~~~~~~~
    Exceptions to be used in the CLI modules.

    :license: MIT, see LICENSE for more details.
"""

import SoftLayer


class CLIHalt(SystemExit):
    """Smoothly halt the execution of the command. No error."""
    def __init__(self, code=0, *args):
        super(CLIHalt, self).__init__(*args)
        self.code = code

    def __str__(self):
        return "<CLIHalt code=%s %s>" % (self.code, self.args)


class CLIAbort(CLIHalt):
    """Halt the execution of the command. Gives an exit code of 2."""
    def __init__(self, msg, *args):
        super(CLIAbort, self).__init__(code=2, *args)
        self.message = msg


class ArgumentError(CLIAbort):
    """Halt the execution of the command because of invalid arguments."""
    def __init__(self, msg, *args):
        super(ArgumentError, self).__init__(msg, *args)
        self.message = "Argument Error: %s" % msg


class InvalidCommand(SoftLayer.SoftLayerError):
    """Raised when trying to use a command that does not exist."""
    def __init__(self, module_name, command_name, *args):
        self.module_name = module_name
        self.command_name = command_name
        cmd_str = module_name
        if command_name is not None:
            cmd_str = '%s %s' % (module_name, command_name)
        SoftLayer.SoftLayerError.__init__(self,
                                          'Invalid command: "%s"' % cmd_str,
                                          *args)
