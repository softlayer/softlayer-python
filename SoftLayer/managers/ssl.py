"""
    SoftLayer.SSL
    ~~~~~~~~~~~~~
    SSL Manager/helpers

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: BSD, see LICENSE for more details.
"""


class SSLManager(object):
    """ Manages SSL certificates. """

    def __init__(self, client):
        """ SSLManager initialization.

        :param SoftLayer.API.Client client: an API client instance

        """
        self.client = client
        self.ssl = self.client['Security_Certificate']

    def list_certs(self, method='all'):
        """ List all certificates.

        :param method:  # TODO: explain this param

        """
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
        """ Creates a new certificate.

        :param certificate:  # TODO: is this a dict?

        """
        return self.ssl.createObject(certificate)

    def remove_certificate(self, id):
        """ Removes a certificate.

        :param integer id: a certificate ID to remove

        """
        return self.ssl.deleteObject(id=id)

    def edit_certificate(self, certificate):
        """ Updates a certificate with the included options. The provided dict
        must include an 'id' key and value corresponding to the certificate ID
        that should be updated.

        :param dict certificate: the certificate to update.

        """
        return self.ssl.editObject(certificate, id=certificate['id'])

    def get_certificate(self, id):
        """ Gets a certificate with the ID specified.

        :param integer id: the certificate ID to retrieve

        """
        return self.ssl.getObject(id=id)
