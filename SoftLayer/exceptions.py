"""
    SoftLayer.exceptions
    ~~~~~~~~~~~~~~~~~~~~
    Exceptions used throughout the library

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: MIT, see LICENSE for more details.
"""


class SoftLayerError(StandardError):
    " The base SoftLayer error. "


class Unauthenticated(SoftLayerError):
    " Unauthenticated "


class SoftLayerAPIError(SoftLayerError):
    """ SoftLayerAPIError is an exception raised whenever an error is returned
    from the API.

    Provides faultCode and faultString properties.
    """
    def __init__(self, faultCode, faultString, *args):
        SoftLayerError.__init__(self, faultString, *args)
        self.faultCode = faultCode
        self.reason = self.faultString = faultString

    def __repr__(self):
        return '<%s(%s): %s>' % \
            (self.__class__.__name__, self.faultCode, self.faultString)

    def __str__(self):
        return '%s(%s): %s' % \
            (self.__class__.__name__, self.faultCode, self.faultString)


class ParseError(SoftLayerAPIError):
    " Parse Error "


class ServerError(SoftLayerAPIError):
    " Server Error "


class ApplicationError(SoftLayerAPIError):
    " Application Error "


class RemoteSystemError(SoftLayerAPIError):
    " System Error "


class TransportError(SoftLayerAPIError):
    " Transport Error "


class NotWellFormed(ParseError):
    pass


class UnsupportedEncoding(ParseError):
    pass


class InvalidCharacter(ParseError):
    pass


class SpecViolation(ServerError):
    pass


class MethodNotFound(ServerError):
    pass


class InvalidMethodParameters(ServerError):
    pass


class InternalError(ServerError):
    pass


class DNSZoneNotFound(SoftLayerError):
    pass
