"""List IPSEC VPN Tunnel Context Details."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command()
@click.argument('context_id', type=int)
@click.option('-i',
              '--include',
              default=[],
              multiple=True,
              type=click.Choice(['at', 'is', 'rs', 'sr', 'ss']),
              help='Include additional resources')
@environment.pass_env
def cli(env, context_id, include):
    """List IPSEC VPN tunnel context details.

    Additional resources can be joined using multiple instances of the
    include option, for which the following choices are available.

    \b
    at: address translations
    is: internal subnets
    rs: remote subnets
    sr: statically routed subnets
    ss: service subnets
    """
    mask = _get_tunnel_context_mask(('at' in include),
                                    ('is' in include),
                                    ('rs' in include),
                                    ('sr' in include),
                                    ('ss' in include))
    manager = SoftLayer.IPSECManager(env.client)
    context = manager.get_tunnel_context(context_id, mask=mask)

    env.out('Context Details:')
    env.fout(_get_context_table(context))

    for relation in include:
        if relation == 'at':
            env.out('Address Translations:')
            env.fout(_get_address_translations_table(
                context.get('addressTranslations', [])))
        elif relation == 'is':
            env.out('Internal Subnets:')
            env.fout(_get_subnets_table(context.get('internalSubnets', [])))
        elif relation == 'rs':
            env.out('Remote Subnets:')
            env.fout(_get_subnets_table(context.get('customerSubnets', [])))
        elif relation == 'sr':
            env.out('Static Subnets:')
            env.fout(_get_subnets_table(context.get('staticRouteSubnets', [])))
        elif relation == 'ss':
            env.out('Service Subnets:')
            env.fout(_get_subnets_table(context.get('serviceSubnets', [])))


def _get_address_translations_table(address_translations):
    """Yields a formatted table to print address translations.

    :param List[dict] address_translations: List of address translations.
    :return Table: Formatted for address translation output.
    """
    table = formatting.Table(['id',
                              'static IP address',
                              'static IP address id',
                              'remote IP address',
                              'remote IP address id',
                              'note'])
    for address_translation in address_translations:
        table.add_row([address_translation.get('id', ''),
                       address_translation.get('internalIpAddressRecord', {})
                       .get('ipAddress', ''),
                       address_translation.get('internalIpAddressId', ''),
                       address_translation.get('customerIpAddressRecord', {})
                       .get('ipAddress', ''),
                       address_translation.get('customerIpAddressId', ''),
                       address_translation.get('notes', '')])
    return table


def _get_subnets_table(subnets):
    """Yields a formatted table to print subnet details.

    :param List[dict] subnets: List of subnets.
    :return Table: Formatted for subnet output.
    """
    table = formatting.Table(['id',
                              'network identifier',
                              'cidr',
                              'note'])
    for subnet in subnets:
        table.add_row([subnet.get('id', ''),
                       subnet.get('networkIdentifier', ''),
                       subnet.get('cidr', ''),
                       subnet.get('note', '')])
    return table


def _get_tunnel_context_mask(address_translations=False,
                             internal_subnets=False,
                             remote_subnets=False,
                             static_subnets=False,
                             service_subnets=False):
    """Yields a mask object for a tunnel context.

    All exposed properties on the tunnel context service are included in
    the constructed mask. Additional joins may be requested.

    :param bool address_translations: Whether to join the context's address
           translation entries.
    :param bool internal_subnets: Whether to join the context's internal
           subnet associations.
    :param bool remote_subnets: Whether to join the context's remote subnet
           associations.
    :param bool static_subnets: Whether to join the context's statically
           routed subnet associations.
    :param bool service_subnets: Whether to join the SoftLayer service
           network subnets.
    :return string: Encoding for the requested mask object.
    """
    entries = ['id',
               'accountId',
               'advancedConfigurationFlag',
               'createDate',
               'customerPeerIpAddress',
               'modifyDate',
               'name',
               'friendlyName',
               'internalPeerIpAddress',
               'phaseOneAuthentication',
               'phaseOneDiffieHellmanGroup',
               'phaseOneEncryption',
               'phaseOneKeylife',
               'phaseTwoAuthentication',
               'phaseTwoDiffieHellmanGroup',
               'phaseTwoEncryption',
               'phaseTwoKeylife',
               'phaseTwoPerfectForwardSecrecy',
               'presharedKey']
    if address_translations:
        entries.append('addressTranslations[internalIpAddressRecord[ipAddress],'
                       'customerIpAddressRecord[ipAddress]]')
    if internal_subnets:
        entries.append('internalSubnets')
    if remote_subnets:
        entries.append('customerSubnets')
    if static_subnets:
        entries.append('staticRouteSubnets')
    if service_subnets:
        entries.append('serviceSubnets')
    return '[mask[{}]]'.format(','.join(entries))


def _get_context_table(context):
    """Yields a formatted table to print context details.

    :param dict context: The tunnel context
    :return Table: Formatted for tunnel context output
    """
    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'

    table.add_row(['id', context.get('id', '')])
    table.add_row(['name', context.get('name', '')])
    table.add_row(['friendly name', context.get('friendlyName', '')])
    table.add_row(['internal peer IP address',
                   context.get('internalPeerIpAddress', '')])
    table.add_row(['remote peer IP address',
                   context.get('customerPeerIpAddress', '')])
    table.add_row(['advanced configuration flag',
                   context.get('advancedConfigurationFlag', '')])
    table.add_row(['preshared key', context.get('presharedKey', '')])
    table.add_row(['phase 1 authentication',
                   context.get('phaseOneAuthentication', '')])
    table.add_row(['phase 1 diffie hellman group',
                   context.get('phaseOneDiffieHellmanGroup', '')])
    table.add_row(['phase 1 encryption', context.get('phaseOneEncryption', '')])
    table.add_row(['phase 1 key life', context.get('phaseOneKeylife', '')])
    table.add_row(['phase 2 authentication',
                   context.get('phaseTwoAuthentication', '')])
    table.add_row(['phase 2 diffie hellman group',
                   context.get('phaseTwoDiffieHellmanGroup', '')])
    table.add_row(['phase 2 encryption', context.get('phaseTwoEncryption', '')])
    table.add_row(['phase 2 key life', context.get('phaseTwoKeylife', '')])
    table.add_row(['phase 2 perfect forward secrecy',
                   context.get('phaseTwoPerfectForwardSecrecy', '')])
    table.add_row(['created', context.get('createDate')])
    table.add_row(['modified', context.get('modifyDate')])
    return table
