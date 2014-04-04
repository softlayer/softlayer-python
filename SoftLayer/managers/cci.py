import warnings
from SoftLayer.managers.vs import VSManager


class CCIManager(VSManager):
    def __init__(self, client):
        super(CCIManager, self).__init__(client)
        warnings.warn("The CCIManager class has been replaced with VSManager.",
                      DeprecationWarning)
