"""
    SoftLayer.consts
    ~~~~~~~~~~~~~~~~
    Contains constants used throughout the library

    :license: MIT, see LICENSE for more details.
"""
VERSION = 'v6.0.2'
API_PUBLIC_ENDPOINT = 'https://api.softlayer.com/xmlrpc/v3.1/'
API_PRIVATE_ENDPOINT = 'https://api.service.softlayer.com/xmlrpc/v3.1/'
API_PUBLIC_ENDPOINT_REST = 'https://api.softlayer.com/rest/v3.1/'
API_PRIVATE_ENDPOINT_REST = 'https://api.service.softlayer.com/rest/v3.1/'
API_EMPLOYEE_ENDPOINT = 'https://internal.app0lb.dal10.softlayer.local/v3/internal/xmlrpc/'
USER_AGENT = "softlayer-python/%s" % VERSION
CONFIG_FILE = "~/.softlayer"
