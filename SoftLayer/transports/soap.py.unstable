"""
    SoftLayer.transports.soap
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    SOAP Style transport library

    :license: MIT, see LICENSE for more details.
"""

import logging

# Try to import zeep, make sure its softlayer_zeep, error otherwise
from zeep import Client
from zeep import Settings
from zeep import Transport
from zeep import xsd

from zeep.cache import SqliteCache
from zeep.helpers import serialize_object
from zeep.plugins import HistoryPlugin

from SoftLayer import consts
from SoftLayer import exceptions


# pylint: disable=too-many-instance-attributes
class SoapTransport(object):
    """SoapTransport."""

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
        self.soapns = "http://api.service.softlayer.com/soap/v3.1/"

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

        # Must define headers like this because otherwise the objectMask header doesn't work
        # because it isn't sent in with a namespace.
        xsd_userauth = xsd.Element(
            f"{{{self.soapns}}}authenticate",
            xsd.ComplexType([
                xsd.Element(f'{{{self.soapns}}}username', xsd.String()),
                xsd.Element(f'{{{self.soapns}}}apiKey', xsd.String())
            ])
        )
        # factory = client.type_factory(f"{self.soapns}")
        the_mask = client.get_type(f"{{{self.soapns}}}SoftLayer_ObjectMask")
        xsd_mask = xsd.Element(
            f"{{{self.soapns}}}SoftLayer_ObjectMask", the_mask
        )

        # Object Filter
        filter_type = client.get_type(f"{{{self.soapns}}}{request.service}ObjectFilter")
        xsd_filter = xsd.Element(
            f"{{{self.soapns}}}{request.service}ObjectFilter", filter_type
        )

        # Result Limit
        xsd_resultlimit = xsd.Element(
            f"{{{self.soapns}}}resultLimit",
            xsd.ComplexType([
                xsd.Element('limit', xsd.String()),
                xsd.Element('offset', xsd.String()),
            ])
        )

        # Might one day want to support unauthenticated requests, but for now assume user auth.
        headers = [
            xsd_userauth(username=request.transport_user, apiKey=request.transport_password),
        ]

        if request.limit:
            headers.append(xsd_resultlimit(limit=request.limit, offset=request.offset))
        if request.mask:
            headers.append(xsd_mask(mask=request.mask))
        if request.filter:
            # The ** here forces python to treat this dict as properties
            headers.append(xsd_filter(**request.filter))

        if request.identifier:
            init_param = f"{request.service}InitParameters"
            init_paramtype = client.get_type(f"{{{self.soapns}}}{init_param}")
            xsdinit_param = xsd.Element(
                f"{{{self.soapns}}}{init_param}", init_paramtype
            )
            # Might want to check if its an id or globalIdentifier at some point, for now only id.
            headers.append(xsdinit_param(id=request.identifier))

        # NEXT Add params... maybe
        try:
            method = getattr(client.service, request.method)
        except AttributeError as ex:
            message = f"{request.service}::{request.method}() does not exist in {self.soapns}{request.service}?wsdl"
            raise exceptions.TransportError(404, message) from ex

        result = method(_soapheaders=headers)

        # NEXT GET A WAY TO FIND TOTAL ITEMS

        try:
            method_return = f"{request.method}Return"
            serialize = serialize_object(result)
            if serialize.get('body'):
                return serialize['body'][method_return]
            else:
                # Some responses (like SoftLayer_Account::getObject) don't have a body?
                return serialize
        except KeyError as ex:
            message = f"Error serializeing response\n{result}\n{ex}"
            raise exceptions.TransportError(500, message)

    def print_reproduceable(self, request):
        """Prints out the minimal python code to reproduce a specific request

        The will also automatically replace the API key so its not accidently exposed.

        :param request request: Request object
        """
        log = logging.getLogger(__name__)
        log.DEBUG(f"{request.service}::{request.method}()")
        return self.history.last_sent
