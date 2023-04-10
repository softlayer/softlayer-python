"""Create a CDN domain mapping."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.option('--hostname', required=True, help="To route requests to your website, enter the hostname for your"
              "website, for example, www.example.com or app.example.com.")
@click.option('--origin', required=True, help="Your server IP address or hostname.")
@click.option('--origin-type', default="server", type=click.Choice(['server', 'storage']), show_default=True,
              help="The origin type. Note: If OriginType is storage then OriginHost is take as Endpoint")
@click.option('--http', help="Http port")
@click.option('--https', help="Https port")
@click.option('--bucket-name', help="Bucket name")
@click.option('--cname', help="Enter a globally unique subdomain. The full URL becomes the CNAME we use to configure"
              " your DNS. If no value is entered, we will generate a CNAME for you.")
@click.option('--header', help="The edge server uses the host header in the HTTP header to communicate with the"
              " Origin host. It defaults to Hostname.")
@click.option('--path', help="Give a path relative to the domain provided, which can be used to reach this Origin."
              " For example, 'articles/video' => 'www.example.com/articles/video")
@click.option('--ssl', default="dvSan", type=click.Choice(['dvSan', 'wilcard']), help="A DV SAN Certificate allows"
              " HTTPS traffic over your personal domain, but it requires a domain validation to prove ownership."
              " A wildcard certificate allows HTTPS traffic only when using the CNAME given.")
@environment.pass_env
def cli(env, hostname, origin, origin_type, http, https, bucket_name, cname, header, path, ssl):
    """Create a CDN domain mapping."""
    if not http and not https:
        raise exceptions.CLIAbort('Is needed http or https options')

    manager = SoftLayer.CDNManager(env.client)
    cdn = manager.create_cdn(hostname, origin, origin_type, http, https, bucket_name, cname, header, path, ssl)

    table = formatting.Table(['Name', 'Value'])
    table.add_row(['CDN Unique ID', cdn.get('uniqueId')])
    if bucket_name:
        table.add_row(['Bucket Name', cdn.get('bucketName')])
    table.add_row(['Hostname', cdn.get('domain')])
    table.add_row(['Header', cdn.get('header')])
    table.add_row(['IBM CNAME', cdn.get('cname')])
    table.add_row(['Akamai CNAME', cdn.get('akamaiCname')])
    table.add_row(['Origin Host', cdn.get('originHost')])
    table.add_row(['Origin Type', cdn.get('originType')])
    table.add_row(['Protocol', cdn.get('protocol')])
    table.add_row(['Http Port', cdn.get('httpPort')])
    table.add_row(['Https Port', cdn.get('httpsPort')])
    table.add_row(['Certificate Type', cdn.get('certificateType')])
    table.add_row(['Provider', cdn.get('vendorName')])
    table.add_row(['Path', cdn.get('path')])

    env.fout(table)
