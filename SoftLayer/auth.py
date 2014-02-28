"""
    SoftLayer.auth
    ~~~~~~~~~~~~~~
    Module with the supported auth mechanisms for the SoftLayer API

    :license: MIT, see LICENSE for more details.
"""
__all__ = ['BasicAuthentication', 'TokenAuthentication', 'AuthenticationBase']


class AuthenticationBase(object):
    """ A base authentication class intended to be overridden """
    def get_headers(self):
        """ Return a dictionary of XML-RPC headers to be inserted for
            authentication """
        raise NotImplementedError


class TokenAuthentication(AuthenticationBase):
    """ Token-based authentication class.

        :param user_id int: a user's id
        :param auth_token str: a user's auth token, attained through
                               User_Customer::getPortalLoginToken
    """
    def __init__(self, user_id, auth_token):
        self.user_id = user_id
        self.auth_token = auth_token

    def get_headers(self):
        """ Returns token-based auth headers """
        return {
            'authenticate': {
                'complexType': 'PortalLoginToken',
                'userId': self.user_id,
                'authToken': self.auth_token,
            }
        }

    def __repr__(self):
        return "<TokenAuthentication: %s %s>" % (self.user_id, self.auth_token)


class BasicAuthentication(AuthenticationBase):
    """ Token-based authentication class.

        :param username str: a user's username
        :param api_key str: a user's API key
    """
    def __init__(self, username, api_key):
        self.username = username
        self.api_key = api_key

    def get_headers(self):
        """ Returns token-based auth headers """
        return {
            'authenticate': {
                'username': self.username,
                'apiKey': self.api_key,
            }
        }

    def __repr__(self):
        return "<BasicAuthentication: %s>" % (self.username)
