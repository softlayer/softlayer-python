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
            mask = """mask[virtualGuestMembers[id,virtualGuest[hostname,domain,provisionDate]], terminationPolicy,
                   virtualGuestMemberCount, virtualGuestMemberTemplate[sshKeys],
                   policies[id,name,createDate,cooldown,actions,triggers,scaleActions],
                   networkVlans[networkVlanId,networkVlan[networkSpace,primaryRouter[hostname]]],
                   loadBalancers, regionalGroup[locations]]"""
        return self.client.call('SoftLayer_Scale_Group', 'getObject', id=identifier, mask=mask)

    def get_policy(self, identifier, mask=None):
        if not mask:
            mask = """mask[cooldown, createDate, id, name, actions, triggers[type]

            ]"""

        return self.client.call('SoftLayer_Scale_Policy', 'getObject', id=identifier, mask=mask)
