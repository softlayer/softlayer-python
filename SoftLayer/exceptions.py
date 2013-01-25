

class SoftLayerError(StandardError):
    """
        The base SoftLayer error.
    """
    def __init__(self, reason, *args):
        StandardError.__init__(self, reason, *args)
        self.reason = reason

    def __repr__(self):
        return 'SoftLayerError: %s' % self.reason

    def __str__(self):
        return 'SoftLayerError: %s' % self.reason
