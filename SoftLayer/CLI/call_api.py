"""Call arbitrary API endpoints."""
import click

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
            raise exceptions.CLIAbort('Failed to find valid operation for: %s'
                                      % _filter)

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


@click.command('call', short_help="Call arbitrary API endpoints.")
@click.argument('service')
@click.argument('method')
@click.argument('parameters', nargs=-1)
@click.option('--id', '_id', help="Init parameter")
@helpers.multi_option('--filter', '-f', '_filters',
                      help="Object filters. This should be of the form: "
                      "'property=value' or 'nested.property=value'. Complex "
                      "filters like betweenDate are not currently supported.")
@click.option('--mask', help="String-based object mask")
@click.option('--limit', type=click.INT, help="Result limit")
@click.option('--offset', type=click.INT, help="Result offset")
@click.option('--output-python / --no-output-python',
              help="Show python example code instead of executing the call")
@environment.pass_env
def cli(env, service, method, parameters, _id, _filters, mask, limit, offset,
        output_python=False):
    """Call arbitrary API endpoints with the given SERVICE and METHOD.

    \b
    Examples:
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
    """

    args = [service, method] + list(parameters)
    kwargs = {
        'id': _id,
        'filter': _build_filters(_filters),
        'mask': mask,
        'limit': limit,
        'offset': offset,
    }

    if output_python:
        env.out(_build_python_example(args, kwargs))
    else:
        result = env.client.call(*args, **kwargs)
        env.fout(formatting.iter_to_table(result))
