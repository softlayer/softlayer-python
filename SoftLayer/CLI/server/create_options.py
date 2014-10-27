"""Server order options for a given chassis."""
# :license: MIT, see LICENSE for more details.
import os

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.CLI import server

import click


@click.command()
@click.argument('chassis-id')
@environment.pass_env
def cli(env, chassis_id):
    """Server order options for a given chassis."""

    mgr = SoftLayer.HardwareManager(env.client)

    table = formatting.KeyValueTable(['Name', 'Value'])
    table.align['Name'] = 'r'
    table.align['Value'] = 'l'

    found = False
    for chassis in mgr.get_available_dedicated_server_packages():
        if chassis_id == str(chassis[0]):
            found = True
            break

    if not found:
        raise exceptions.CLIAbort('Invalid chassis specified.')

    ds_options = mgr.get_dedicated_server_create_options(chassis_id)

    # Determine if this is a "Bare Metal Instance" or regular server
    bmc = False
    if chassis_id == str(mgr.get_bare_metal_package_id()):
        bmc = True

    results = server.get_create_options(ds_options, 'datacenter')[0]
    table.add_row([results[0], formatting.listing(sorted(results[1]))])

    # BMC options
    if bmc:
        # CPU and memory options
        results = server.get_create_options(ds_options, 'server_core')
        memory_cpu_table = formatting.Table(['memory', 'cpu'])
        for result in results:
            memory_cpu_table.add_row([
                result[0],
                formatting.listing(
                    [item[0] for item in sorted(
                        result[1], key=lambda x: int(x[0])
                    )])])
        table.add_row(['memory/cpu', memory_cpu_table])

    # Normal hardware options
    else:
        # CPU options
        results = server.get_create_options(ds_options, 'cpu')
        cpu_table = formatting.Table(['ID', 'Description'])
        cpu_table.align['ID'] = 'r'
        cpu_table.align['Description'] = 'l'

        for result in sorted(results, key=lambda x: x[1]):
            cpu_table.add_row([result[1], result[0]])
        table.add_row(['cpu', cpu_table])

        # Memory options
        results = server.get_create_options(ds_options, 'memory')[0]
        table.add_row([results[0], formatting.listing(
            item[0] for item in sorted(results[1]))])

        # Disk controller options
        results = server.get_create_options(ds_options, 'disk_controller')[0]
        table.add_row([results[0], formatting.listing(
            item[0] for item in sorted(results[1],))])

    # Disk options
    results = server.get_create_options(ds_options, 'disk')[0]
    table.add_row([
        results[0],
        formatting.listing(
            [item[0] for item in sorted(results[1])],
            separator=os.linesep
        )])

    # Operating system options
    results = server.get_create_options(ds_options, 'os')
    for result in results:
        table.add_row([
            result[0],
            formatting.listing(
                [item[0] for item in sorted(result[1])],
                separator=os.linesep
            )])

    # NIC options
    results = server.get_create_options(ds_options, 'nic')
    for result in results:
        table.add_row([result[0], formatting.listing(
            item[0] for item in sorted(result[1],))])

    return table
