"""List all options for ordering a block storage."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI.command import SLCommand
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting

volume_size = ['20', '40', '80', '100', '250', '500', '1000', '2000-3000', '4000-7000', '8000-9000', '10000-12000']


@click.command(cls=SLCommand)
@environment.pass_env
def cli(env):
    """List all options for ordering a block storage"""

    network_manager = SoftLayer.NetworkManager(env.client)
    datacenters = network_manager.get_datacenter()

    table = formatting.Table(['Name', 'Value'], title='Volume table')

    table.add_row(['Storage Type', 'performance,endurance'])
    table.add_row(['Size (GB)', str(volume_size)])
    table.add_row(['OS Type', 'HYPER_V,LINUX,VMWARE,WINDOWS_2008,WINDOWS_GPT,WINDOWS,XEN'])
    iops_table = formatting.Table(['Size (GB)', '20', '40', '80', '100', '250', '500', '1000', '2000-3000',
                                   '4000-7000', '8000-9000', '10000-12000'], title='IOPS table')
    snapshot_table = formatting.Table(['Storage Size (GB)', 'Available Snapshot Size (GB)'], title="Snapshot table")

    datacenter_str = ','.join([str(dc['longName']) for dc in datacenters])
    iops_table.add_row(['Size (GB)', *volume_size])
    iops_table.add_row(['Min IOPS', '100', '100', '100', '100', '100', '100', '100', '200', '300', '500', '1000'])
    iops_table.add_row(['Max IOPS', '1000', '2000', '4000', '6000', '6000', '6000 or 10000', '6000 or 20000',
                        '6000 or 40000', '6000 or 48000', '6000 or 48000', '6000 or 48000'])
    # table.add_row(['iops', iops_table])
    table.add_row(['Tier', '0.25,2,4,10'])
    table.add_row(['location', datacenter_str])

    snapshot_table.add_row(['20', '0,5,10,20'])
    snapshot_table.add_row(['40', '0,5,10,20,40'])
    snapshot_table.add_row(['80', '0,5,10,20,40,60,80'])
    snapshot_table.add_row(['100', '0,5,10,20,40,60,80,100'])
    snapshot_table.add_row(['250', '0,5,10,20,40,60,80,100,150,200,250'])
    snapshot_table.add_row(['500', '0,5,10,20,40,60,80,100,150,200,250,300,350,400,450,500'])
    snapshot_table.add_row(['1000', '0,5,10,20,40,60,80,100,150,200,250,300,350,400,450,500,600,700,1000'])
    snapshot_table.add_row(['2000-3000', '0,5,10,20,40,60,80,100,150,200,250,300,350,400,450,500,600,700,1000,2000'])
    snapshot_table.add_row(
        ['4000-7000', '0,5,10,20,40,60,80,100,150,200,250,300,350,400,450,500,600,700,1000,2000,4000'])
    snapshot_table.add_row(
        ['8000-9000', '0,5,10,20,40,60,80,100,150,200,250,300,350,400,450,500,600,700,1000,2000,4000'])
    snapshot_table.add_row(
        ['10000-12000', '0,5,10,20,40,60,80,100,150,200,250,300,350,400,450,500,600,700,1000,2000,4000'])

    # table.add_row(['Snapshot Size (GB)', snapshot_table])
    table.add_row(['Note:',
                   'IOPs limit above 6000 available in select data centers, refer to:'
                   'http://knowledgelayer.softlayer.com/articles/new-ibm-block-and-file-storage-location-and-features'])
    env.fout(table)
    env.fout(iops_table)
    env.fout(snapshot_table)
