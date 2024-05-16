"""
    SoftLayer.transports.transport
    ~~~~~~~~~~~~~~~~~~~~
    Common functions for transporting API requests

    :license: MIT, see LICENSE for more details.
"""
import base64
import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


from SoftLayer import utils


def get_session(user_agent):
    """Sets up urllib sessions"""

    client = requests.Session()
    client.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': user_agent,
    })
    retry = Retry(total=3, connect=1, backoff_factor=1)
    adapter = HTTPAdapter(max_retries=retry)
    client.mount('https://', adapter)
    return client


# transports.Request does have a lot of instance attributes. :(
# pylint: disable=too-many-instance-attributes
class Request(object):
    """Transport request object."""

    def __init__(self):
        #: API service name. E.G. SoftLayer_Account
        self.service = None

        #: API method name. E.G. getObject
        self.method = None

        #: API Parameters.
        self.args = tuple()

        #: API headers, used for authentication, masks, limits, offsets, etc.
        self.headers = {}

        #: Transport user.
        self.transport_user = None

        #: Transport password.
        self.transport_password = None

        #: Transport headers.
        self.transport_headers = {}

        #: False -> Don't verify the SSL certificate
        #: True -> Verify the SSL certificate
        #: Path String -> Verify the SSL certificate with the .pem file at path
        self.verify = None

        #: Client certificate file path. (Used by X509Authentication)
        self.cert = None

        #: InitParameter/identifier of an object.
        self.identifier = None

        #: SoftLayer mask (dict or string).
        self.mask = None

        #: SoftLayer Filter (dict).
        self.filter = None

        #: Integer result limit.
        self.limit = None

        #: Integer result offset.
        self.offset = None

        #: Integer call start time
        self.start_time = None

        #: Integer call end time
        self.end_time = None

        #: String full url
        self.url = None

        #: String result of api call
        self.result = None

        #: String payload to send in
        self.payload = None

        #: Exception any exceptions that got caught
        self.exception = None

    def __repr__(self):
        """Prints out what this call is all about"""
        pretty_mask = utils.clean_string(self.mask)
        pretty_filter = self.filter
        clean_args = self.args
        # Passwords can show up here, so censor them before logging.
        if self.method in ["performExternalAuthentication", "refreshEncryptedToken", "getPortalLoginToken"]:
            clean_args = "*************"
        param_string = (f"id={self.identifier}, mask='{pretty_mask}', filter='{pretty_filter}', args={clean_args}, "
                        f"limit={self.limit}, offset={self.offset}")
        return "{service}::{method}({params})".format(
            service=self.service, method=self.method, params=param_string)


class SoftLayerListResult(list):
    """A SoftLayer API list result."""

    def __init__(self, items=None, total_count=0):

        #: total count of items that exist on the server. This is useful when
        #: paginating through a large list of objects.
        self.total_count = total_count
        super().__init__(items)


def _proxies_dict(proxy):
    """Makes a proxy dict appropriate to pass to requests."""
    if not proxy:
        return None
    return {'http': proxy, 'https': proxy}


def _format_object_mask(objectmask):
    """Format the new style object mask.

    This wraps the user mask with mask[USER_MASK] if it does not already
    have one. This makes it slightly easier for users.

    :param objectmask: a string-based object mask

    """
    objectmask = objectmask.strip()

    if (not objectmask.startswith('mask') and
            not objectmask.startswith('[') and
            not objectmask.startswith('filteredMask')):
        objectmask = "mask[%s]" % objectmask
    return objectmask


class ComplexEncoder(json.JSONEncoder):
    """ComplexEncoder helps jsonencoder deal with byte strings"""

    def default(self, o):
        """Encodes o as JSON"""

        # Base64 encode bytes type objects.
        if isinstance(o, bytes):
            base64_bytes = base64.b64encode(o)
            return base64_bytes.decode("utf-8")
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, o)
