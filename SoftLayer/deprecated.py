"""
    SoftLayer.deprecated
    ~~~~~~~~~~~~~~~~~~~~
    This is where deprecated APIs go for their eternal slumber

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
from warnings import warn
from SoftLayer.exceptions import SoftLayerError


class DeprecatedClientMixin():
    """ This mixin is to be used in SoftLayer.Client so all of these methods
        should be available to the client but are all deprecated.
    """

    def __init__(self, id=None, username=None, api_key=None, **kwargs):

        if id is not None:
            warn("The id parameter is deprecated", DeprecationWarning)
            self.set_init_parameter(int(id))

        if username and api_key:
            self._headers['authenticate'] = {
                'username': username.strip(),
                'apiKey': api_key.strip(),
            }

    def __getattr__(self, name):
        """ Attempt a SoftLayer API call.

        Use this as a catch-all so users can call SoftLayer API methods
        directly against their client object. If the property or method
        relating to their client object doesn't exist then assume the user is
        attempting a SoftLayer API call and return a simple function that makes
        an XML-RPC call.

        :param name: method name

        ..  deprecated:: 2.0.0

        """
        warn("deprecated", DeprecationWarning)
        if name in ["__name__", "__bases__"]:
            raise AttributeError("'Obj' object has no attribute '%s'" % name)

        def call_handler(*args, **kwargs):
            if self._service_name is None:
                raise SoftLayerError(
                    "Service is not set on Client instance.")
            kwargs['headers'] = self._headers
            return self.call(self._service_name, name, *args, **kwargs)
        return call_handler

    def add_raw_header(self, name, value):
        """ Set HTTP headers for API calls.

        :param name: the header name
        :param value: the header value

        ..  deprecated:: 2.0.0

        """
        warn("deprecated", DeprecationWarning)
        self._raw_headers[name] = value

    def add_header(self, name, value):
        """ Set a SoftLayer API call header.

        :param name: the header name
        :param value: the header value

        ..  deprecated:: 2.0.0

        """
        warn("deprecated", DeprecationWarning)
        name = name.strip()
        if name is None or name == '':
            raise SoftLayerError('Please specify a header name.')

        self._headers[name] = value

    def remove_header(self, name):
        """ Remove a SoftLayer API call header.

        :param name: the header name

        ..  deprecated:: 2.0.0

        """
        warn("deprecated", DeprecationWarning)
        if name in self._headers:
            del self._headers[name.strip()]

    def set_authentication(self, username, api_key):
        """ Set user and key to authenticate a SoftLayer API call.

        Use this method if you wish to bypass the API_USER and API_KEY class
        constants and set custom authentication per API call.

        See https://manage.softlayer.com/Administrative/apiKeychain for more
        information.

        :param username: the username to authenticate with
        :param api_key: the user's API key

        ..  deprecated:: 2.0.0

        """
        warn("deprecated", DeprecationWarning)
        self.add_header('authenticate', {
            'username': username.strip(),
            'apiKey': api_key.strip(),
        })

    def set_init_parameter(self, id):
        """ Set an initialization parameter header.

        Initialization parameters instantiate a SoftLayer API service object to
        act upon during your API method call. For instance, if your account has
        a server with ID number 1234, then setting an initialization parameter
        of 1234 in the SoftLayer_Hardware_Server Service instructs the API to
        act on server record 1234 in your method calls.

        See http://sldn.softlayer.com/article/Using-Initialization-Parameters-SoftLayer-API  # NOQA
        for more information.

        :param id: the ID of the SoftLayer API object to instantiate

        ..  deprecated:: 2.0.0

        """
        warn("deprecated", DeprecationWarning)
        self.add_header(self._service_name + 'InitParameters', {
            'id': int(id)
        })

    def set_object_mask(self, mask):
        """ Set an object mask to a SoftLayer API call.

        Use an object mask to retrieve data related your API call's result.
        Object masks are skeleton objects, or strings that define nested
        relational properties to retrieve along with an object's local
        properties. See
        http://sldn.softlayer.com/article/Using-Object-Masks-SoftLayer-API
        for more information.

        :param mask: the object mask you wish to define

        ..  deprecated:: 2.0.0

        """
        warn("deprecated", DeprecationWarning)
        header = 'SoftLayer_ObjectMask'

        if isinstance(mask, dict):
            header = '%sObjectMask' % self._service_name

        self.add_header(header, {'mask': mask})

    def set_result_limit(self, limit, offset=0):
        """ Set a result limit on a SoftLayer API call.

        Many SoftLayer API methods return a group of results. These methods
        support a way to limit the number of results retrieved from the
        SoftLayer API in a way akin to an SQL LIMIT statement.

        :param limit: the number of results to limit a SoftLayer API call to
        :param offset: An optional offset at which to begin a SoftLayer API
                       call's returned result

        ..  deprecated:: 2.0.0

        """
        warn("deprecated", DeprecationWarning)
        self.add_header('resultLimit', {
            'limit': int(limit),
            'offset': int(offset)
        })
