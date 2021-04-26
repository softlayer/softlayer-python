"""
    SoftLayer.auth
    ~~~~~~~~~~~~~~
    Module with the supported auth mechanisms for the SoftLayer API

    :license: MIT, see LICENSE for more details.
"""
# pylint: disable=no-self-use

__all__ = [
    'BasicAuthentication',
    'TokenAuthentication',
    'BasicHTTPAuthentication',
    'AuthenticationBase',
]


class AuthenticationBase(object):
    """A base authentication class intended to be overridden."""

    def get_request(self, request):
        """Receives request options and returns request options.

            :param options dict: dictionary of request options

        """
        return request

    def get_headers(self):
        """Return a dictionary of headers to be inserted for authentication.

        .. deprecated:: 3.3.0
           Use :func:`get_options` instead.
        """
        return {}


class TokenAuthentication(AuthenticationBase):
    """Token-based authentication class.

        :param user_id int: a user's id
        :param auth_token str: a user's auth token, attained through
                               User_Customer::getPortalLoginToken
    """

    def __init__(self, user_id, auth_token):
        self.user_id = user_id
        self.auth_token = auth_token

    def get_request(self, request):
        """Sets token-based auth headers."""
        request.headers['authenticate'] = {
            'complexType': 'PortalLoginToken',
            'userId': self.user_id,
            'authToken': self.auth_token,
        }
        return request

    def __repr__(self):
        return "TokenAuthentication(%r)" % self.user_id


class BasicAuthentication(AuthenticationBase):
    """Token-based authentication class.

        :param username str: a user's username
        :param api_key str: a user's API key
    """

    def __init__(self, username, api_key):
        self.username = username
        self.api_key = api_key

    def get_request(self, request):
        """Sets token-based auth headers."""

        # See https://cloud.ibm.com/docs/iam?topic=iam-iamapikeysforservices for why this is the way it is
        if self.username == 'apikey':
            request.transport_user = self.username
            request.transport_password = self.api_key
        else:
            request.headers['authenticate'] = {
                'username': self.username,
                'apiKey': self.api_key,
            }

        return request

    def __repr__(self):
        return "BasicAuthentication(username=%r)" % self.username


class BasicHTTPAuthentication(AuthenticationBase):
    """Token-based authentication class.

        :param username str: a user's username
        :param api_key str: a user's API key
    """

    def __init__(self, username, api_key):
        self.username = username
        self.api_key = api_key

    def get_request(self, request):
        """Sets token-based auth headers."""
        request.transport_user = self.username
        request.transport_password = self.api_key
        return request

    def __repr__(self):
        return "BasicHTTPAuthentication(username=%r)" % self.username


class BearerAuthentication(AuthenticationBase):
    """Bearer Token authentication class.

        :param username str: a user's username, not really needed but all the others use it.
        :param api_key str: a user's IAM Token
    """

    def __init__(self, username, token, r_token=None):
        """For using IBM IAM authentication

        :param username str: Not really needed, will be set to their current username though for logging
        :param token str: the IAM Token
        :param r_token str: The refresh Token, optional
        """
        self.username = username
        self.api_key = token
        self.r_token = r_token

    def get_request(self, request):
        """Sets token-based auth headers."""
        request.transport_headers['Authorization'] = 'Bearer {}'.format(self.api_key)
        request.transport_user = self.username
        return request

    def __repr__(self):
        return "BearerAuthentication(username={}, token={})".format(self.username, self.api_key)
