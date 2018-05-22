"""Virtual Servers."""
# :license: MIT, see LICENSE for more details.

import re

import click

MEMORY_RE = re.compile(r"^(?P<amount>[0-9]+)(?P<unit>g|gb|m|mb)?$")


class MemoryType(click.ParamType):
    """Memory type."""
    name = 'integer'

    def convert(self, value, param, ctx):  # pylint: disable=inconsistent-return-statements
        """Validate memory argument. Returns the memory value in megabytes."""
        matches = MEMORY_RE.match(value.lower())
        if matches is None:
            self.fail('%s is not a valid value for memory amount' % value, param, ctx)
        amount_str, unit = matches.groups()
        amount = int(amount_str)
        if unit in [None, 'm', 'mb']:
            # Assume the user intends gigabytes if they specify a number < 1024
            if amount < 1024:
                return amount * 1024
            else:
                if amount % 1024 != 0:
                    self.fail('%s is not an integer that is divisable by 1024' % value, param, ctx)
                return amount
        elif unit in ['g', 'gb']:
            return amount * 1024


MEM_TYPE = MemoryType()
