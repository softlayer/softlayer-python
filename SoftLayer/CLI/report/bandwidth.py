"""Bandwidth report for every pool/server."""
import click

from SoftLayer.CLI.command import SLCommand as SLCommand
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer import utils


@click.command(cls=SLCommand, short_help="Bandwidth report for every pool/server")
@environment.pass_env
def cli(env):
    """Bandwidth report for every pool/server.

    This reports on the total data transfered for each virtual sever, hardware
    server and bandwidth pool.
    https://cloud.ibm.com/classic-bandwidth
    """

    table = formatting.Table([
        'Id',
        'Device name',
        'Location',
        'Allocation',
        'Data in',
        'Data out',
        'Total usage',
        'Pool',
        'Tags',
    ])

    mask = """mask[resource(SoftLayer_Hardware)[id,bandwidthAllocation,bandwidthAllotmentDetail[id,bandwidthAllotment
    [id,bandwidthAllotmentTypeId,name]],billingItem[id,createDate,lastBillDate],datacenter[id,name],
    fullyQualifiedDomainName,inboundPublicBandwidthUsage,outboundPublicBandwidthUsage,primaryIpAddress,tagReferences
    [id,tag[id,name]]],resource(SoftLayer_Network_Application_Delivery_Controller)[id,billingItem[id,
    bandwidthAllocation[id,amount],bandwidthAllotmentDetail[id,bandwidthAllotment[id,bandwidthAllotmentTypeId,name]]
    ,createDate,lastBillDate],datacenter[id,name],name,outboundPublicBandwidthUsage,primaryIpAddress,tagReferences
    [id,tag[id,name]]],resource(SoftLayer_Virtual_Guest)[id,bandwidthAllocation,bandwidthAllotmentDetail[id,
    bandwidthAllotment[id,bandwidthAllotmentTypeId,name]],billingItem[id,createDate,lastBillDate],datacenter[id,name
    ],fullyQualifiedDomainName,inboundPublicBandwidthUsage,outboundPublicBandwidthUsage,primaryIpAddress,
    tagReferences[id,tag[id,name]]]]"""

    search_string = """_objectType:SoftLayer_Hardware,SoftLayer_Virtual_Guest,
    SoftLayer_Network_Application_Delivery_Controller _sort:[fullyQualifiedDomainName:asc]"""

    servers = env.client.call(
        'Search', 'advancedSearch',
        search_string,
        mask=mask,
        iter=True
    )

    for server in servers:
        resource = server.get('resource')

        device_name = utils.lookup(resource, 'fullyQualifiedDomainName')
        if not device_name:
            device_name = utils.lookup(resource, 'name')

        bandwidth_allocation = utils.lookup(resource, 'bandwidthAllocation')
        if bandwidth_allocation != '0':
            if bandwidth_allocation is not None:
                bandwidth_allocation = formatting.convert_sizes(
                    bandwidth_allocation, round_result=True)
            else:
                bandwidth_allocation = 'Unlimited'
        else:
            bandwidth_allocation = 'Pay-As-You-Go'

        in_bandwidth_public = formatting.convert_sizes(utils.lookup(resource, 'inboundPublicBandwidthUsage'))

        out_bandwidth_public = formatting.convert_sizes(utils.lookup(resource, 'outboundPublicBandwidthUsage'))

        total_bandwidth_public = formatting.sum_sizes(in_bandwidth_public, out_bandwidth_public)

        if bandwidth_allocation != 'Unlimited' and bandwidth_allocation != 'Pay-As-You-Go':
            pool = utils.lookup(resource, 'bandwidthAllotmentDetail', 'bandwidthAllotment', 'name')
        else:
            pool = 'Not Applicable'

        table.add_row([
            utils.lookup(resource, 'id'),
            device_name,
            utils.lookup(resource, 'datacenter', 'name'),
            bandwidth_allocation,
            in_bandwidth_public,
            out_bandwidth_public,
            total_bandwidth_public,
            pool,
            formatting.tags(resource.get('tagReferences')),
        ])

    env.fout(table)
