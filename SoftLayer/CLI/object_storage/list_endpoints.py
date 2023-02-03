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

    table = formatting.Table(['Location/Region', 'Url', 'EndPoint Type', 'Public/Private', 'Legacy'])
    table.align['Location/Region'] = 'l'
    table.align['Url'] = 'l'
    for endpoint in endpoints:
        data = {
            'Location/Region': location_region(endpoint),
            'Url': endpoint['url'],
            'EndPoint Type': end_point_return(endpoint['region']),
            'Public/Private': public_private(endpoint['type']),
            'Legacy': endpoint['legacy']
        }
        final_end_points.append(data)

    final_end_points = sort_endpoint(final_end_points)
    table = add_array_to_table(table, final_end_points)

    env.fout(table)


def add_array_to_table(table, array_datas):
    """Add an array to a table"""
    for array in array_datas:
        table.add_row([array['Location/Region'],
                       array['Url'],
                       array['EndPoint Type'],
                       array['Public/Private'],
                       array['Legacy']])
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
    first_data = 0
    endpoint_type = ''
    if len(endpoints) > 0:
        endpoint_type = endpoints[first_data]['EndPoint Type']
    public = []
    private = []
    array_final = []
    for endpoint in endpoints:
        if endpoint['EndPoint Type'] != endpoint_type:
            endpoint_type = endpoint['EndPoint Type']
            array_final = array_final + public + private
            public.clear()
            private.clear()
        if endpoint['Public/Private'] == 'Public':
            public.append(endpoint)
        else:
            private.append(endpoint)

    array_final = array_final + public + private
    return array_final
