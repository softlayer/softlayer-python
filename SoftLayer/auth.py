"""
    SoftLayer.auth
    ~~~~~~~~~~~~~~
    Module with the supported auth mechanisms for the SoftLayer API

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: MIT, see LICENSE for more details.
"""
__all__ = ['BasicAuthentication', 'TokenAuthentication', 'AuthenticationBase']


class AuthenticationBase(object):
    def get_headers(self):
        raise NotImplementedError


class TokenAuthentication(AuthenticationBase):
    def __init__(self, user_id, auth_token):
        self.user_id = user_id
        self.auth_token = auth_token

    def get_headers(self):
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
    def __init__(self, username, api_key):
        self.username = username
        self.api_key = api_key

    def get_headers(self):
        return {
            'authenticate': {
                'username': self.username,
                'apiKey': self.api_key,
            }
        }

    def __repr__(self):
        return "<BasicAuthentication: %s>" % (self.username)
