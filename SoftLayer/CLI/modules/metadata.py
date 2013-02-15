#!/usr/bin/env python
""" Find details about this machine """

from SoftLayer.CLI import CLIRunnable, Table


class BackendMacAddresses(CLIRunnable):
    """ List all CCI's on the account"""
    action = 'backend_mac_addresses'

    @staticmethod
    def execute(client, args):
        t = Table(['backend mac addresses'])
        ips = client['Resource_Metadata'].getBackendMacAddresses()
        for ip in ips:
            t.add_row([ip])
        return t
