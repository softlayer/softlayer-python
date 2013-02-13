__all__ = ["SSLManager"]


class SSLManager(object):
    def __init__(self, client):
        """SSLManager

            :param client: SoftLayer.API.Client
        """
        self.client = client
        self.ssl = self.client['Security_Certificate']

    def list_certs(self, method='all'):
        ssl = self.client['Account']
        methods = {
            'all': 'getSecurityCertificates',
            'expired': 'getExpiredSecurityCertificates',
            'valid': 'getValidSecurityCertificates'
        }

        mask = "mask[id, commonName, validityDays, notes]"
        func = getattr(ssl, methods[method])
        return func(mask=mask)

    def add_certificate(self, certificate):
        """SSLManager

            :param client: SoftLayer.API.Client
        """

        return self.ssl.createObject(certificate)

    def remove_certificate(self, cert_id):
        """SSLManager

            :param client: SoftLayer.API.Client
        """
        return self.ssl.deleteObject(id=cert_id)

    def edit_certificate(self, certificate):
        """SSLManager

            :param client: SoftLayer.API.Client
        """

        return self.ssl.editObject(certificate, id=certificate['id'])

    def get_certificate(self, cert_id):
        return self.ssl.getObject(id=cert_id)
