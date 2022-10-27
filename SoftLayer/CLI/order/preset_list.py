"""List package presets."""
# :license: MIT, see LICENSE for more details.

import click

from SoftLayer.CLI.command import SLCommand as SLCommand
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.managers import ordering

COLUMNS = ['Name', 'Key Name', 'Description']


@click.command(cls=SLCommand)
@click.argument('package_keyname')
@click.option('--keyword', help="A word (or string) used to filter preset names.")
@click.option('--prices', '-p', is_flag=True, help='Use --prices to list the server item prices.')
@environment.pass_env
def cli(env, package_keyname, keyword, prices):
    """List package presets.

    .. Note::
        Presets are set CPU / RAM / Disk allotments. You still need to specify required items.
        Some packages do not have presets.
        Cost includes all items in a preset, and may include optional items.

    ::

        # List the presets for Bare Metal servers
        slcli order preset-list BARE_METAL_SERVER

        # List the Bare Metal server presets that include a GPU
        slcli order preset-list BARE_METAL_SERVER --keyword gpu

        # Get a specific flavor for Virtual Server
        slcli order preset-list PUBLIC_CLOUD_SERVER --prices --keyword BL2.56x242x

        # All packages with active presets
        slcli call-api SoftLayer_Product_Package getAllObjects --mask="mask[id,keyName,activePresetCount]" \
--json-filter='{"activePresets":{"operation":"not null"}}'
        ┌───────────────────┬──────┬──────────────────────────────────────────────────────────────────┐
        │ activePresetCount │  id  │                             keyName                              │
        ├───────────────────┼──────┼──────────────────────────────────────────────────────────────────┤
        │         1         │ 144  │                              3U_GPU                              │
        │         6         │ 200  │                        BARE_METAL_SERVER                         │
        │         1         │ 571  │                           NETWORK_VLAN                           │
        │        100        │ 835  │                       PUBLIC_CLOUD_SERVER                        │
        │         6         │ 865  │                     NETWORK_VLAN_FOR_SERVICE                     │
        │         5         │ 885  │                           8U_BI_S2_H4                            │
        │        56         │ 991  │                      TRANSIENT_CLOUD_SERVER                      │
        │        56         │ 1035 │                       SUSPEND_CLOUD_SERVER                       │
        │         9         │ 1045 │                          2U_BI_S3_H2000                          │
        │         7         │ 1075 │                   2U_IC4V_FIXED_CONFIGURATIONS                   │
        │        32         │ 1109 │                           BI_S4_H2000                            │
        │         8         │ 1117 │                           BI_S4_H4000                            │
        │         7         │ 1119 │                           BI_S4_H8000                            │
        │         5         │ 2636 │                    2U_BI_S4_H2000_AEP_ENABLED                    │
        │         5         │ 2676 │                    4U_BI_S4_H4000_AEP_ENABLED                    │
        │         5         │ 2700 │                    4U_BI_S4_H8000_AEP_ENABLED                    │
        │         6         │ 2866 │ ORACLE_APPLICATION_CLUSTER_CASCADE_LAKE_SCALABLE_FAMILY_4_DRIVES │
        │         1         │ 2874 │          ORACLE_APPLICATION_CLUSTER_COFFEE_LAKE_E2174G           │
        └───────────────────┴──────┴──────────────────────────────────────────────────────────────────┘

    """
    click.secho("*NOTICE*: Cost includes all items in a preset, and may include optional items.", fg="yellow")
    manager = ordering.OrderingManager(env.client)

    _filter = {}
    if keyword:
        _filter = {'activePresets': {'name': {'operation': '*= %s' % keyword}}}
    presets = manager.list_presets(package_keyname, filter=_filter)

    if prices:
        table = formatting.Table(['Id', 'Key Name', 'Hourly', 'Monthly', 'Location'])
        table.align = {"Id": "center", "Key Name": "left", "Hourly": "right", "Monthly": "right", "Location": "center"}
        for price in presets:
            locations_list = []
            if price['locations'] != []:
                for location in price['locations']:
                    locations_list.append(location['name'])
                locations = ', '.join(locations_list)
            else:
                locations = "All"
            table.add_row([
                price['id'],
                price['keyName'],
                get_item_price_data(price['prices'], 'hourlyRecurringFee'),
                get_item_price_data(price['prices'], 'recurringFee'),
                locations
            ])

    else:
        table = formatting.Table(COLUMNS)
        for preset in presets:
            table.add_row([
                str(preset['name']).strip(),
                str(preset['keyName']).strip(),
                str(preset['description']).strip()
            ])

    env.fout(table)


def get_item_price_data(prices, item_attribute):
    """Given an SoftLayer_Product_Item_Price, returns its default price data"""
    result = 0.0
    for this_price in prices:
        if item_attribute in this_price:
            result = result + float(this_price[item_attribute])
    return round(result, 3)
