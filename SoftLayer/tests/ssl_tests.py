from SoftLayer.SSL import SSLManager

try:
    import unittest2 as unittest
except ImportError:
    import unittest
from mock import MagicMock, ANY


class SSLTests_unittests(unittest.TestCase):

    def setUp(self):
        self.client = MagicMock()
        self.ssl = SSLManager(self.client)
        self.test_id = 10

    def test_list_certs(self):
        self.ssl.list_certs('valid')
        self.client.__getitem__() \
            .getValidSecurityCertificates.assert_called_once_with(mask=ANY)

        self.ssl.list_certs('expired')
        self.client.__getitem__() \
            .getExpiredSecurityCertificates.assert_called_once_with(mask=ANY)

        self.ssl.list_certs('all')
        self.client.__getitem__() \
            .getSecurityCertificates.assert_called_once_with(mask=ANY)

    def test_add_certificate(self):
        test_cert = {
            'certificate': 'cert',
            'privateKey': 'key',
        }

        self.ssl.add_certificate(test_cert)

        self.client.__getitem__().createObject.assert_called_once_with(
            test_cert)

    def test_remove_certificate(self):
        self.ssl.remove_certificate(self.test_id)
        self.client.__getitem__() \
            .deleteObject.assert_called_once_with(id=self.test_id)

    def test_edit_certificate(self):
        test_cert = {
            'id': self.test_id,
            'certificate': 'cert',
            'privateKey': 'key'
        }

        self.ssl.edit_certificate(test_cert)
        self.client.__getitem__().editObject.assert_called_once_with(
            {
                'id': self.test_id,
                'certificate': 'cert',
                'privateKey': 'key'
            },
            id=self.test_id)

    def test_get_certificate(self):
        self.ssl.get_certificate(self.test_id)
        self.client.__getitem__().getObject.assert_called_once_with(
            id=self.test_id)

