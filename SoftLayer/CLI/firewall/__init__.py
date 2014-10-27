"""Firewalls."""
# :license: MIT, see LICENSE for more details.

from SoftLayer.CLI import exceptions


def parse_id(input_id):
    """Helper package to retrieve the actual IDs.

    :param input_id: the ID provided by the user
    :returns: A list of valid IDs
    """
    key_value = input_id.split(':')

    if len(key_value) != 2:
        raise exceptions.CLIAbort(
            'Invalid ID %s: ID should be of the form xxx:yyy' % input_id)
    return key_value[0], int(key_value[1])
