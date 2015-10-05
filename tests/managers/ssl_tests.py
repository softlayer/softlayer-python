"""
    SoftLayer.tests.managers.ssl_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
import SoftLayer
from SoftLayer import fixtures
from SoftLayer import testing


class SSLTests(testing.TestCase):

    def set_up(self):
        self.ssl = SoftLayer.SSLManager(self.client)
        self.test_id = 10

    def test_list_certs_valid(self):
        result = self.ssl.list_certs('valid')

        self.assertEqual(
            result,
            fixtures.SoftLayer_Account.getValidSecurityCertificates)
        self.assert_called_with('SoftLayer_Account',
                                'getValidSecurityCertificates')

    def test_list_certs_expired(self):
        result = self.ssl.list_certs('expired')

        self.assertEqual(
            result,
            fixtures.SoftLayer_Account.getExpiredSecurityCertificates)
        self.assert_called_with('SoftLayer_Account',
                                'getExpiredSecurityCertificates')

    def test_list_certs_all(self):
        result = self.ssl.list_certs('all')

        self.assertEqual(
            result,
            fixtures.SoftLayer_Account.getSecurityCertificates)
        self.assert_called_with('SoftLayer_Account',
                                'getSecurityCertificates')

    def test_add_certificate(self):
        test_cert = {
            'certificate': 'cert',
            'privateKey': 'key',
        }

        result = self.ssl.add_certificate(test_cert)

        self.assertEqual(result,
                         fixtures.SoftLayer_Security_Certificate.createObject)
        self.assert_called_with('SoftLayer_Security_Certificate',
                                'createObject',
                                args=(test_cert,))

    def test_remove_certificate(self):
        result = self.ssl.remove_certificate(self.test_id)

        self.assertEqual(result, True)
        self.assert_called_with('SoftLayer_Security_Certificate',
                                'deleteObject',
                                identifier=self.test_id)

    def test_edit_certificate(self):
        test_cert = {
            'id': self.test_id,
            'certificate': 'cert',
            'privateKey': 'key'
        }

        result = self.ssl.edit_certificate(test_cert)

        self.assertEqual(result, True)
        args = ({
            'id': self.test_id,
            'certificate': 'cert',
            'privateKey': 'key'
        },)
        self.assert_called_with('SoftLayer_Security_Certificate',
                                'editObject',
                                args=args,
                                identifier=self.test_id)

    def test_get_certificate(self):
        result = self.ssl.get_certificate(self.test_id)

        self.assertEqual(result,
                         fixtures.SoftLayer_Security_Certificate.getObject)
        self.assert_called_with('SoftLayer_Security_Certificate',
                                'getObject',
                                identifier=self.test_id)
