"""Call arbitrary API endpoints."""
import json

import click

from SoftLayer.CLI.command import SLCommand as SLCommand
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer import utils

SPLIT_TOKENS = [
    ('in', ' IN '),
    ('eq', '='),
]


def _build_filters(_filters):
    """Builds filters using the filter options passed into the CLI.

    This only supports the equals keyword at the moment.
    """
    root = utils.NestedDict({})
    for _filter in _filters:
        operation = None
        for operation, token in SPLIT_TOKENS:
            # split "some.key=value" into ["some.key", "value"]
            top_parts = _filter.split(token, 1)
            if len(top_parts) == 2:
                break
        else:
            raise exceptions.CLIAbort('Failed to find valid operation for: %s' % _filter)

        key, value = top_parts
        current = root
        # split "some.key" into ["some", "key"]
        parts = [part.strip() for part in key.split('.')]

        # Actually drill down and add the filter
        for part in parts[:-1]:
            current = current[part]

        if operation == 'eq':
            current[parts[-1]] = utils.query_filter(value.strip())
        elif operation == 'in':
            current[parts[-1]] = {
                'operation': 'in',
                'options': [{
                    'name': 'data',
                    'value': [p.strip() for p in value.split(',')],
                }],
            }

    return root.to_dict()


def _build_python_example(args, kwargs):
    sorted_kwargs = sorted(kwargs.items())

    call_str = 'import SoftLayer\n\n'
    call_str += 'client = SoftLayer.create_client_from_env()\n'
    call_str += 'result = client.call('
    arg_list = [repr(arg) for arg in args]
    arg_list += [key + '=' + repr(value)
                 for key, value in sorted_kwargs if value]
    call_str += ',\n                     '.join(arg_list)
    call_str += ')'

    return call_str


def _validate_filter(ctx, param, value):  # pylint: disable=unused-argument
    """Validates a JSON style object filter"""
    _filter = None
    if value:
        try:
            _filter = json.loads(value)
            if not isinstance(_filter, dict):
                raise exceptions.CLIAbort("\"{}\" should be a JSON object, but is a {} instead.".
                                          format(_filter, type(_filter)))
        except json.JSONDecodeError as error:
            raise exceptions.CLIAbort("\"{}\" is not valid JSON. {}".format(value, error))

    return _filter


def _validate_parameters(ctx, param, value):  # pylint: disable=unused-argument
    """Checks if value is a JSON string, and converts it to a datastructure if that is true"""

    validated_values = []
    for parameter in value:
        if isinstance(parameter, str):
            # looks like a JSON string...
            if '{' in parameter or '[' in parameter:
                try:
                    parameter = json.loads(parameter)
                except json.JSONDecodeError as error:
                    click.secho("{} looked like json, but was invalid, passing to API as is. {}".
                                format(parameter, error), fg='red')
        validated_values.append(parameter)
    return validated_values


@click.command('call', short_help="Call arbitrary API endpoints.", cls=SLCommand)
@click.argument('service')
@click.argument('method')
@click.argument('parameters', nargs=-1, callback=_validate_parameters)
@click.option('--id', '_id', help="Init parameter")
@helpers.multi_option('--filter', '-f', '_filters',
                      help="Object filters. This should be of the form: 'property=value' or 'nested.property=value'."
                           "Complex filters should use --json-filter.")
@click.option('--mask', help="String-based object mask")
@click.option('--limit', type=click.INT, help="Result limit")
@click.option('--offset', type=click.INT, help="Result offset")
@click.option('--orderBy', type=click.STRING,
              help="To set the sort direction, ASC or DESC can be provided."
                   "This should be of the form: '--orderBy nested.property' default DESC or "
                   "'--orderBy nested.property=ASC', e.g. "
                   " --orderBy subnets.id default DESC"
                   " --orderBy subnets.id=ASC")
@click.option('--output-python / --no-output-python',
              help="Show python example code instead of executing the call")
@click.option('--json-filter', callback=_validate_filter,
              help="A JSON string to be passed in as the object filter to the API call. "
                   "Remember to use double quotes (\") for variable names. Can NOT be used with --filter. "
                   "Dont use whitespace outside of strings, or the slcli might have trouble parsing it.")
@environment.pass_env
def cli(env, service, method, parameters, _id, _filters, mask, limit, offset, orderby=None,
        output_python=False, json_filter=None):
    """Call arbitrary API endpoints with the given SERVICE and METHOD.

    For parameters that require a datatype, use a JSON string for that parameter.
    Example::

        slcli call-api Account getObject
        slcli call-api Account getVirtualGuests --limit=10 --mask=id,hostname
        slcli call-api Virtual_Guest getObject --id=12345
        slcli call-api Metric_Tracking_Object getBandwidthData --id=1234 \\
            "2015-01-01 00:00:00" "2015-01-1 12:00:00" public
        slcli call-api Account getVirtualGuests \\
            -f 'virtualGuests.datacenter.name=dal05' \\
            -f 'virtualGuests.maxCpu=4' \\
            --mask=id,hostname,datacenter.name,maxCpu
        slcli call-api Account getVirtualGuests \\
            -f 'virtualGuests.datacenter.name IN dal05,sng01'
        slcli call-api Account getVirtualGuests \\
            --json-filter  '{"virtualGuests":{"hostname":{"operation":"^= test"}}}' --limit=10
        slcli -v call-api SoftLayer_User_Customer addBulkPortalPermission --id=1234567 \\
            '[{"keyName": "NETWORK_MESSAGE_DELIVERY_MANAGE"}]'
        slcli call-api Account getVirtualGuests \\
            --orderBy virttualguests.id=ASC
        slcli call-api SoftLayer_Notification_Occurrence_Event getAllObjects \\
            --json-filter='{"endDate": {"operation": "greaterThanDate", \\
            "options": [{"name":"date", "value": ["10/14/2022"]}]}}' --limit=50
    """

    if _filters and json_filter:
        raise exceptions.CLIAbort("--filter and --json-filter cannot be used together.")

    object_filter = _build_filters(_filters)
    if orderby:
        orderby = utils.build_filter_orderby(orderby)
        object_filter = utils.dict_merge(object_filter, orderby)
    if json_filter:
        object_filter = utils.dict_merge(json_filter, object_filter)

    args = [service, method] + list(parameters)
    kwargs = {
        'id': _id,
        'filter': object_filter,
        'mask': mask,
        'limit': limit,
        'offset': offset,
    }

    if output_python:
        env.python_output(_build_python_example(args, kwargs))
    else:
        result = env.client.call(*args, **kwargs)
        env.fout(formatting.iter_to_table(result))
