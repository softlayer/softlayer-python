"""
    SoftLayer.cci
    ~~~~~~~~~~~~~
    CCIManager to provide backwards compatibility.

    :license: MIT, see LICENSE for more details.
"""
import warnings
from SoftLayer.managers.vs import VSManager


class CCIManager(VSManager):
    """
    Wrapper for the VSManager class to provide backwards compatibility with the
    old CCIManager class.
    """
    def __init__(self, client):
        super(CCIManager, self).__init__(client)
        warnings.warn("The CCIManager class has been replaced with VSManager.",
                      DeprecationWarning)
