"""
    SoftLayer.autoscale
    ~~~~~~~~~~~~
    Autoscale manager

    :license: MIT, see LICENSE for more details.
"""



class AutoScaleManager(object):

    def __init__(self, client):
        self.client = client


    def list(self, mask=None):
        if not mask:
            mask = "mask[status,virtualGuestMemberCount]"

        return self.client.call('SoftLayer_Account', 'getScaleGroups', mask=mask, iter=True)

    def details(self, identifier, mask=None):
        if not mask:
            mask = """mask[virtualGuestMembers, terminationPolicy, policies, virtualGuestMemberCount,
                   networkVlans[networkVlanId,networkVlan[networkSpace,primaryRouter[hostname]]],
                   loadBalancers, regionalGroup[locations]]"""
        return self.client.call('SoftLayer_Scale_Group', 'getObject', id=identifier, mask=mask)