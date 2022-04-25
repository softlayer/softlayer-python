"""
    SoftLayer.transports.soap
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    SOAP Style transport library

    :license: MIT, see LICENSE for more details.
"""
import logging
import re
from string import Template
from zeep import Client, Settings, Transport, xsd
from zeep.helpers import serialize_object
from zeep.cache import SqliteCache
from zeep.plugins import HistoryPlugin
from zeep.wsdl.messages.multiref import process_multiref


import requests

from SoftLayer import consts
from SoftLayer import exceptions

from .transport import _format_object_mask
from .transport import _proxies_dict
from .transport import ComplexEncoder
from .transport import get_session
from .transport import SoftLayerListResult

from pprint import pprint as pp


class SoapTransport(object):
    """XML-RPC transport."""

    def __init__(self, endpoint_url=None, timeout=None, proxy=None, user_agent=None, verify=True):

        # Throw an error for py < 3.6 because of f-strings
        logging.getLogger('zeep').setLevel(logging.ERROR)
        logging.getLogger('zeep.transports').setLevel(logging.DEBUG)
        self.endpoint_url = (endpoint_url or consts.API_PUBLIC_ENDPOINT).rstrip('/')
        self.timeout = timeout or None
        self.proxy = proxy
        self.user_agent = user_agent or consts.USER_AGENT
        self.verify = verify
        self._client = None
        self.history = HistoryPlugin()
        self.soapNS = "http://api.service.softlayer.com/soap/v3.1/"

    def __call__(self, request):
        """Makes a SoftLayer API call against the SOAP endpoint.

        :param request request: Request object
        """

        zeep_settings = Settings(strict=False, xml_huge_tree=True)
        zeep_transport = Transport(cache=SqliteCache(timeout=86400))
        client = Client(f"{self.endpoint_url}/{request.service}?wsdl",
                        settings=zeep_settings, transport=zeep_transport, plugins=[self.history])

        # print(client.wsdl.dump())
        # print("=============== WSDL ==============")
        # MUST define headers like this because otherwise the objectMask header doesn't work
        # because it isn't sent in with a namespace.
        xsdUserAuth = xsd.Element(
            f"{{{self.soapNS}}}authenticate",
            xsd.ComplexType([
                xsd.Element(f'{{{self.soapNS}}}username', xsd.String()),
                xsd.Element(f'{{{self.soapNS}}}apiKey', xsd.String())
            ])
        )
        factory = client.type_factory(f"{self.soapNS}")
        theMask = client.get_type(f"{{{self.soapNS}}}SoftLayer_ObjectMask")
        xsdMask = xsd.Element(
            f"{{{self.soapNS}}}SoftLayer_ObjectMask",
            factory['SoftLayer_ObjectMask']
        )

        # Object Filter
        filterType = client.get_type(f"{{{self.soapNS}}}{request.service}ObjectFilter")
        xsdFilter = xsd.Element(
            f"{{{self.soapNS}}}{request.service}ObjectFilter", filterType
        )

        # Result Limit
        xsdResultLimit = xsd.Element(
            f"{{{self.soapNS}}}resultLimit",
            xsd.ComplexType([
                xsd.Element('limit', xsd.String()),
                xsd.Element('offset', xsd.String()),
            ])
        )

        # Might one day want to support unauthenticated requests, but for now assume user auth.
        headers = [
            xsdUserAuth(username=request.transport_user, apiKey=request.transport_password),
        ]

        if request.limit:
            headers.append(xsdResultLimit(limit=request.limit, offset=request.offset))
        if request.mask:
            headers.append(xsdMask(mask=request.mask))
        if request.filter:
            # The ** here forces python to treat this dict as properties
            headers.append(xsdFilter(**request.filter))

        if request.identifier:
            initParam = f"{request.service}InitParameters"
            initParamType = client.get_type(f"{{{self.soapNS}}}{initParam}")
            xsdInitParam = xsd.Element(
                f"{{{self.soapNS}}}{initParam}", initParamType
            )
            # Might want to check if its an id or globalIdentifier at some point, for now only id.
            headers.append(xsdInitParam(id=request.identifier))

        # TODO Add params... maybe
        try:
            method = getattr(client.service, request.method)
        except AttributeError as ex:
            message = f"{request.service}::{request.method}() does not exist in {self.soapNS}{request.service}?wsdl"
            raise exceptions.TransportError(404, message) from ex

        result = method(_soapheaders=headers)
        # result = client.service.getObject(_soapheaders=headers)

        # process_multiref(result['body']['getAllObjectsReturn'])

        # print("^^^ RESULT ^^^^^^^")

        # TODO GET A WAY TO FIND TOTAL ITEMS
        # print(result['header']['totalItems']['amount'])
        # print(" ^^ ITEMS ^^^ ")

        try:
            methodReturn = f"{request.method}Return"
            serialize = serialize_object(result)
            if serialize.get('body'):
                return serialize['body'][methodReturn]
            else:
                # Some responses (like SoftLayer_Account::getObject) don't have a body?
                return serialize
        except KeyError as e:
            message = f"Error serializeing response\n{result}\n"
            raise exceptions.TransportError(500, message)

    def print_reproduceable(self, request):
        """Prints out the minimal python code to reproduce a specific request

        The will also automatically replace the API key so its not accidently exposed.

        :param request request: Request object
        """

        return self.history.last_sent
