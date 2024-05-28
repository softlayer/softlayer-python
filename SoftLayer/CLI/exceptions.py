"""
    SoftLayer.CLI.exceptions
    ~~~~~~~~~~~~~~~~~~~~~~~~
    Exceptions to be used in the CLI modules.

    :license: MIT, see LICENSE for more details.
"""


# pylint: disable=keyword-arg-before-vararg
class CLIHalt(SystemExit):
    """Smoothly halt the execution of the command. No error."""

    def __init__(self, code=0, *args):
        super().__init__(*args)
        self.code = code

    def __str__(self):
        message = getattr(self, 'message')
        return f"<CLIHalt code={self.code} msg={message}>"
    __repr__ = __str__


class CLIAbort(CLIHalt):
    """Halt the execution of the command. Gives an exit code of 2."""

    def __init__(self, msg, *args):
        super().__init__(code=2, *args)
        self.message = msg

    def __str__(self):
        message = getattr(self, 'message')
        return f"<CLIAbort code={self.code} msg={message}>"
    __repr__ = __str__


class ArgumentError(CLIAbort):
    """Halt the execution of the command because of invalid arguments."""

    def __init__(self, msg, *args):
        super().__init__(msg, *args)
        self.message = "Argument Error: %s" % msg

    def __str__(self):
        message = getattr(self, 'message')
        return f"<ArgumentError code={self.code} msg={message}>"
    __repr__ = __str__
