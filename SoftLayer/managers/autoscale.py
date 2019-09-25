"""
    SoftLayer.autoscale
    ~~~~~~~~~~~~
    Autoscale manager

    :license: MIT, see LICENSE for more details.
"""



class AutoScaleManager(object):

    def __init__(self, client):
        self.client = client


    def list(self):
        print("LISTING....")
        return True