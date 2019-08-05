"""
    SoftLayer.tests.managers.loadbal_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import SoftLayer
from SoftLayer import testing


class LoadBalancerTests(testing.TestCase):

    def set_up(self):
        self.lb_mgr = SoftLayer.LoadBalancerManager(self.client)
