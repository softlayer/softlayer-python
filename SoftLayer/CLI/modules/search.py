"""
usage: sl search [<command>] [<args>...] [options]

Search for API data objects

Examples:
    sl search
    sl search types
    sl search -t cci,ticket
    sl search -t cci,hardware -s dal05

The available commands are:
  None            No command results in a prompt for the search
                   string that you want to use for the search query.
  types           List available types to narrow search.
"""
# :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
# :license: BSD, see LICENSE for more details.
# SoftLayer/CLI/modules

from textwrap import TextWrapper
from SoftLayer import SearchManager
from SoftLayer.utils import console_input
from SoftLayer.CLI import (
    CLIRunnable,
    Table,
    get_simple_type,
    get_api_type,
    CLIAbort,
    NestedDict,
    blank,
    FormattedItem
)


class SearchString(CLIRunnable):
    """
usage: sl search [-s=SEARCH_STRING] [--types=TYPES] [options]

Search Data

Examples:
    sl search
    sl search -t cci,ticket
    sl search -t cci,hardware -s dal05

Filters:
  -s=SEARCH_STRING  The search string or query to use, must be within quotes.
  -t --types=TYPES  Object types to search for, comma seperated.

Search SoftLayer API object data using plain language DSL. The primary objective
is to make it easier to find something. If you just use 'sl search' it will prompt
you for a search string to use to search against all available data types.
"""
    action = None
    default_column_width = 60
    possible_name_properties = [
        'fullyQualifiedDomainName',
        'name',
        'title',
        'ipAddress',
        'vlanNumber'
    ]

    def execute(self, args):
        service = SearchManager(self.client)

        if args.get('-s'):
            query = args.get('-s').strip()
        else:
            query = self.env.input('\n Search String: ').strip()

        if args.get('--types'):
            simple_types = args.get('--types').split(',')
            types = [get_api_type(x) for x in simple_types]
        else:
            types = service.get_search_types()
            # Remove Event Logs, I want to support these in a seperate method
            if 'SoftLayer_Event_Log' in types:
                types.remove('SoftLayer_Event_Log')

        if not query:
            query = '*'

        results = service.search(query, types)

        if results:
            results_table = Table(['Id', 'Type', 'Name'])
            results_table.align['Name'] = 'l'

            wrapper = TextWrapper(width=self.default_column_width, expand_tabs=False)

            for result in results:
                result = NestedDict(result)

                identifier = result['resource'].get('id') or blank()
                resource_type = get_simple_type(result['resourceType'])

                for field in self.possible_name_properties:
                    if result['resource'].get(field):
                        value = result['resource'].get(field)
                        name = FormattedItem(value, '\n'.join(wrapper.wrap(value)))
                        break
                else:
                    name = blank()

                results_table.add_row([identifier, resource_type, name])

            return results_table

        raise CLIAbort("No objects found matching: %s" % query)


class SearchTypes(CLIRunnable):
    """
usage: sl search types [options]

List types available for search.

Examples:
    sl search types

Get a list of types that are available for search. You can pass these
types to the 'sl search' command to narrow down results.
"""
    action = 'types'

    def execute(self, args):
        service = SearchManager(self.client)

        results = service.get_search_types()

        if results:
            results_table = Table(['Type'])
            results_table.align['Type'] = 'l'

            # Remove Event Logs, I want to support these in a seperate method
            if 'SoftLayer_Event_Log' in results:
                results.remove('SoftLayer_Event_Log')

            for result in results:
                results_table.add_row([get_simple_type(result)])

            return results_table

        raise CLIAbort("No types found!")
