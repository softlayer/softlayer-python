"""List Object Storage endpoints."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@environment.pass_env
def cli(env, identifier):
    """List object storage endpoints."""

    mgr = SoftLayer.ObjectStorageManager(env.client)
    endpoints = mgr.list_endpoints(identifier)

    final_end_points = []

    table = formatting.Table(['Legacy', 'EndPoint Type', 'Public/Private', 'Location/Region', 'Url'])
    for endpoint in endpoints:
        data = [endpoint['legacy'], end_point_return(endpoint['region']), public_private(endpoint['type']),
                location_region(endpoint), endpoint['url']]
        final_end_points.append(data)

    final_end_points = sort_endpoint(final_end_points)
    table = add_array_to_table(table, final_end_points)

    env.fout(table)


def add_array_to_table(table, array_datas):
    """Add an array to a table"""
    for array in array_datas:
        table.add_row([array[0], array[1], array[2], array[3], array[4]])
    return table


def end_point_return(endpoint):
    """Returns end point type"""
    if endpoint == 'singleSite':
        return 'Single Site'
    if endpoint == 'regional':
        return 'Region'
    return 'Cross Region'


def public_private(data):
    """Returns public or private in capital letter"""
    if data == 'public':
        return 'Public'
    return 'Private'


def location_region(endpoint):
    """Returns location if it exists otherwise region"""
    if utils.lookup(endpoint, 'location'):
        return endpoint['location']
    return endpoint['region']


def sort_endpoint(endpoints):
    """Sort the all endpoints for public or private"""
    endpoint_type = ''
    if len(endpoints) > 0:
        endpoint_type = endpoints[0][1]
    public = []
    private = []
    array_final = []
    for endpoint in endpoints:
        if endpoint[1] != endpoint_type:
            endpoint_type = endpoint[1]
            array_final = array_final + public + private
            public.clear()
            private.clear()
        if endpoint[2] == 'Public':
            public.append(endpoint)
        else:
            private.append(endpoint)

    array_final = array_final + public + private
    return array_final
