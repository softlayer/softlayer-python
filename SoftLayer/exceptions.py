"""
    SoftLayer.exceptions
    ~~~~~~~~~~~~~~~~~~~~
    Exceptions used throughout the library

    :license: MIT, see LICENSE for more details.
"""
# pylint: disable=C0103


class SoftLayerError(Exception):
    """The base SoftLayer error."""


class Unauthenticated(SoftLayerError):
    """Unauthenticated."""


class IAMError(SoftLayerError):
    """Errors from iam.cloud.ibm.com"""

    def __init__(self, fault_code, fault_string, url=None):
        SoftLayerError.__init__(self, fault_string)
        self.faultCode = fault_code
        self.faultString = fault_string
        self.url = url

    def __repr__(self):
        return "{} ({}): {}".format(self.url, self.faultCode, self.faultString)

    def __str__(self):
        return "{} ({}): {}".format(self.url, self.faultCode, self.faultString)


class SoftLayerAPIError(SoftLayerError):
    """SoftLayerAPIError is an exception raised during API errors.

    Provides faultCode and faultString properties.
    """

    def __init__(self, fault_code, fault_string, *args):
        SoftLayerError.__init__(self, fault_string, *args)
        self.faultCode = fault_code
        self.reason = self.faultString = fault_string

    def __repr__(self):
        return '<%s(%s): %s>' % (self.__class__.__name__, self.faultCode, self.faultString)

    def __str__(self):
        return '%s(%s): %s' % (self.__class__.__name__, self.faultCode, self.faultString)


class ParseError(SoftLayerAPIError):
    """Parse Error."""


class ServerError(SoftLayerAPIError):
    """Server Error."""


class ApplicationError(SoftLayerAPIError):
    """Application Error."""


class RemoteSystemError(SoftLayerAPIError):
    """System Error."""


class TransportError(SoftLayerAPIError):
    """Transport Error."""


# XMLRPC Errors
class NotWellFormed(ParseError):
    """Request was not well formed."""


class UnsupportedEncoding(ParseError):
    """Encoding not supported."""


class InvalidCharacter(ParseError):
    """There was an invalid character."""


class SpecViolation(ServerError):
    """There was a spec violation."""


class MethodNotFound(SoftLayerAPIError):
    """Method name not found."""


class InvalidMethodParameters(SoftLayerAPIError):
    """Invalid method paramters."""


class InternalError(ServerError):
    """Internal Server Error."""
