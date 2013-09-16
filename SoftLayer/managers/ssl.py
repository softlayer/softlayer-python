"""
    SoftLayer.ssl
    ~~~~~~~~~~~~~
    SSL Manager/helpers

    :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
    :license: MIT, see LICENSE for more details.
"""


class SSLManager(object):
    """
    Manages SSL certificates.

    :param SoftLayer.API.Client client: an API client instance
    """

    def __init__(self, client):
        #: A valid `SoftLayer.API.Client` object that will be used for all
        #: actions.
        self.client = client
        #: Reference to the SoftLayer_Security_Certificate API object.
        self.ssl = self.client['Security_Certificate']

    def list_certs(self, method='all'):
        """ List all certificates.

        :param string method: The type of certificates to list. Options are
                              'all', 'expired', and 'valid'.
        :returns: A list of dictionaries representing the requested SSL certs.

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

        :param dict certificate: A dictionary representing the parts of the
                                 certificate. See SLDN for more information.

        """
        return self.ssl.createObject(certificate)

    def remove_certificate(self, id):
        """ Removes a certificate.

        :param integer id: a certificate ID to remove

        """
        return self.ssl.deleteObject(id=id)

    def edit_certificate(self, certificate):
        """ Updates a certificate with the included options.

        The provided dict must include an 'id' key and value corresponding to
        the certificate ID that should be updated.

        :param dict certificate: the certificate to update.

        """
        return self.ssl.editObject(certificate, id=certificate['id'])

    def get_certificate(self, id):
        """ Gets a certificate with the ID specified.

        :param integer id: the certificate ID to retrieve

        """
        return self.ssl.getObject(id=id)
