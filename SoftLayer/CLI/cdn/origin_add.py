"""Create an origin pull mapping."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('unique_id')
@click.argument('origin')
@click.argument('path')
@click.option('--origin-type', '-t',
              type=click.Choice(['server', 'storage']),
              help='The origin type.',
              default='server',
              show_default=True)
@click.option('--header', '-H',
              type=click.STRING,
              help='The host header to communicate with the origin.')
@click.option('--bucket-name', '-b',
              type=click.STRING,
              help="The name of the available resource [required if --origin-type=storage]")
@click.option('--http-port', '-p',
              type=click.INT,
              help="The http port number. [http or https is required]")
@click.option('--https-port', '-s',
              type=click.INT,
              help="The https port number. [http or https is required]"
              )
@click.option('--protocol', '-P',
              type=click.STRING,
              help="The protocol used by the origin.",
              default='http',
              show_default=True)
@click.option('--optimize-for', '-o',
              type=click.Choice(['web', 'video', 'file', 'dynamic']),
              help="Performance configuration",
              default='web',
              show_default=True)
@click.option('--dynamic-path', '-d',
              help="The path that Akamai edge servers periodically fetch the test object from."
              "example = /detection-test-object.html")
@click.option('--compression', '-i',
              help="Enable or disable compression of JPEG images for requests over certain network conditions.",
              default='true',
              show_default=True)
@click.option('--prefetching', '-g',
              help="Enable or disable the embedded object prefetching feature.",
              default='true',
              show_default=True)
@click.option('--extensions', '-e',
              type=click.STRING,
              help="File extensions that can be stored in the CDN, example: 'jpg, png, pdf'")
@click.option('--cache-query', '-c',
              type=click.STRING,
              help="Cache query rules with the following formats:\n"
                   "'ignore-all', 'include: <query-names>', 'ignore: <query-names>'",
              default="include-all",
              show_default=True)
@environment.pass_env
def cli(env, unique_id, origin, path, origin_type, header,
        bucket_name, http_port, https_port, protocol, optimize_for,
        dynamic_path, compression, prefetching,
        extensions, cache_query):
    """Create an origin path for an existing CDN mapping.

    For more information see the following documentation: \n
    https://cloud.ibm.com/docs/infrastructure/CDN?topic=CDN-manage-your-cdn#adding-origin-path-details
    """

    manager = SoftLayer.CDNManager(env.client)

    if origin_type == 'storage' and not bucket_name:
        raise exceptions.ArgumentError('[-b | --bucket-name] is required when [-t | --origin-type] is "storage"')

    result = manager.add_origin(unique_id, origin, path, dynamic_path, origin_type=origin_type,
                                header=header, http_port=http_port, https_port=https_port, protocol=protocol,
                                bucket_name=bucket_name, file_extensions=extensions,
                                optimize_for=optimize_for,
                                compression=compression, prefetching=prefetching,
                                cache_query=cache_query)

    table = formatting.Table(['Item', 'Value'])
    table.align['Item'] = 'r'
    table.align['Value'] = 'r'

    table.add_row(['CDN Unique ID', result['mappingUniqueId']])

    if origin_type == 'storage':
        table.add_row(['Bucket Name', result['bucketName']])

    table.add_row(['Origin', result['origin']])
    table.add_row(['Origin Type', result['originType']])
    table.add_row(['Header', result['header']])
    table.add_row(['Path', result['path']])
    table.add_row(['Http Port', result['httpPort']])
    table.add_row(['Https Port', result['httpsPort']])
    table.add_row(['Cache Key Rule', result['cacheKeyQueryRule']])
    table.add_row(['Configuration', result['performanceConfiguration']])
    table.add_row(['Status', result['status']])

    env.fout(table)
