"""
    SoftLayer.exceptions
    ~~~~~~~~~~~~~~~~~~~~
    Exceptions used throughout the library

    :license: MIT, see LICENSE for more details.
"""


class SoftLayerError(Exception):
    """ The base SoftLayer error. """


class Unauthenticated(SoftLayerError):
    """ Unauthenticated """


class SoftLayerAPIError(SoftLayerError):
    """ SoftLayerAPIError is an exception raised whenever an error is returned
    from the API.

    Provides faultCode and faultString properties.
    """
    def __init__(self, faultCode, faultString, *args):
        SoftLayerError.__init__(self, faultString, *args)
        self.faultCode = faultCode  # pylint: disable=C0103
        self.reason = self.faultString = faultString  # pylint: disable=C0103

    def __repr__(self):
        return '<%s(%s): %s>' % \
            (self.__class__.__name__, self.faultCode, self.faultString)

    def __str__(self):
        return '%s(%s): %s' % \
            (self.__class__.__name__, self.faultCode, self.faultString)


class ParseError(SoftLayerAPIError):
    """ Parse Error """


class ServerError(SoftLayerAPIError):
    """ Server Error """


class ApplicationError(SoftLayerAPIError):
    """ Application Error """


class RemoteSystemError(SoftLayerAPIError):
    """ System Error """


class TransportError(SoftLayerAPIError):
    """ Transport Error """


# XMLRPC Errors
class NotWellFormed(ParseError):
    """ Request was not well formed """
    pass


class UnsupportedEncoding(ParseError):
    """ Encoding not supported """
    pass


class InvalidCharacter(ParseError):
    """ There was an invalid character """
    pass


class SpecViolation(ServerError):
    """ There was a spec violation """
    pass


class MethodNotFound(ServerError):
    """ Method name not found """
    pass


class InvalidMethodParameters(ServerError):
    """ Invalid method paramters """
    pass


class InternalError(ServerError):
    """ Internal Server Error """
    pass


class DNSZoneNotFound(SoftLayerError):
    """ DNS Zone was not found """
    pass
