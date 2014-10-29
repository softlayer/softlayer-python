"""Load balancers."""

from SoftLayer.CLI import exceptions


def parse_id(input_id):
    """Parse the load balancer kind and actual id from the "kind:id" form."""
    parts = input_id.split(':')
    if len(parts) != 2:
        raise exceptions.CLIAbort(
            'Invalid ID %s: ID should be of the form "kind:id"' % input_id)
    return parts[0], int(parts[1])
