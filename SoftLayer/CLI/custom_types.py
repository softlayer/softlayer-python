"""
    SoftLayer.CLI.custom_types
    ~~~~~~~~~~~~~~~~~~~~~~~~
    Custom type declarations extending click.ParamType

    :license: MIT, see LICENSE for more details.
"""

import click


class NetworkParamType(click.ParamType):
    """Validates a network parameter type and converts to a tuple.

    todo: Implement to ipaddress.ip_network once the ipaddress backport
          module can be added as a dependency or is available on all
          supported python versions.
    """
    name = 'network'

    def convert(self, value, param, ctx):
        try:
            # Inlined from python standard ipaddress module
            # https://docs.python.org/3/library/ipaddress.html
            address = str(value).split('/')
            if len(address) != 2:
                raise ValueError("Only one '/' permitted in %r" % value)

            ip_address, cidr = address
            return (ip_address, int(cidr))
        except ValueError:
            self.fail('{} is not a valid network'.format(value), param, ctx)
