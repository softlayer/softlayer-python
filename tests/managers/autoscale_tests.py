"""
    SoftLayer.tests.managers.autoscale_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""

from SoftLayer.managers.autoscale import AutoScaleManager
from SoftLayer import testing


class AutoScaleTests(testing.TestCase):

    def set_up(self):
        self.autoscale = AutoScaleManager(self.client)

    def test_autoscale_list(self):
        self.autoscale.list()

        self.assert_called_with(
            'SoftLayer_Account',
            'getScaleGroups'
        )

    def test_autoscale_list_with_mask(self):
        self.autoscale.list(mask='mask[status,virtualGuestMemberCount]')

        self.assert_called_with(
            'SoftLayer_Account',
            'getScaleGroups'
        )

    def test_autoscale_details(self):
        self.autoscale.details(11111)

        self.assert_called_with(
            'SoftLayer_Scale_Group',
            'getObject',
            identifier=11111
        )

    def test_autoscale_details_with_mask(self):
        self.autoscale.details(11111, mask='mask[virtualGuestMembers[id,virtualGuest[hostname,domain,provisionDate]], '
                                           'terminationPolicy,virtualGuestMemberCount]')

        self.assert_called_with(
            'SoftLayer_Scale_Group',
            'getObject',
            identifier=11111
        )

    def test_autoscale_policy(self):
        self.autoscale.get_policy(11111)

        self.assert_called_with(
            'SoftLayer_Scale_Policy',
            'getObject',
            identifier=11111
        )

    def test_autoscale_policy_with_mask(self):
        self.autoscale.get_policy(11111, mask='mask[cooldown, createDate, id, name, actions, triggers[type]]')

        self.assert_called_with(
            'SoftLayer_Scale_Policy',
            'getObject',
            identifier=11111
        )

    def test_autoscale_scale(self):
        self.autoscale.scale(11111, 3)

        self.assert_called_with(
            'SoftLayer_Scale_Group',
            'scale',
            identifier=11111
        )

    def test_autoscale_scaleTo(self):
        self.autoscale.scale_to(11111, 3)

        self.assert_called_with(
            'SoftLayer_Scale_Group',
            'scaleTo',
            identifier=11111
        )

    def test_autoscale_getLogs(self):
        self.autoscale.get_logs(11111)

        self.assert_called_with(
            'SoftLayer_Scale_Group',
            'getLogs',
            identifier=11111
        )

    def test_autoscale_get_virtual_guests(self):
        self.autoscale.get_virtual_guests(11111)

        self.assert_called_with(
            'SoftLayer_Scale_Group',
            'getVirtualGuestMembers',
            identifier=11111,
            mask=None
        )

    def test_autoscale_get_virtual_guests_mask(self):
        test_mask = "mask[id]"
        self.autoscale.get_virtual_guests(11111, mask=test_mask)

        self.assert_called_with(
            'SoftLayer_Scale_Group',
            'getVirtualGuestMembers',
            identifier=11111,
            mask=test_mask
        )

    def test_edit_object(self):
        template = {'name': 'test'}
        self.autoscale.edit(12345, template)
        self.assert_called_with(
            'SoftLayer_Scale_Group',
            'editObject',
            args=(template,),
            identifier=12345)
