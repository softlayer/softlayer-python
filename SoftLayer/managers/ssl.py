"""
    SoftLayer.ssl
    ~~~~~~~~~~~~~
    SSL Manager/helpers

    :license: MIT, see LICENSE for more details.
"""


class SSLManager(object):
    """Manages SSL certificates.

    :param SoftLayer.API.Client client: an API client instance

    Example::

       # Initialize the Manager.
       # env variables. These can also be specified in ~/.softlayer,
       # or passed directly to SoftLayer.Client()
       # SL_USERNAME = YOUR_USERNAME
       # SL_API_KEY = YOUR_API_KEY
       import SoftLayer
       client = SoftLayer.Client()
       mgr = SoftLayer.SSLManager(client)

    """

    def __init__(self, client):
        self.client = client
        self.ssl = self.client['Security_Certificate']

    def list_certs(self, method='all'):
        """List all certificates.

        :param string method: The type of certificates to list. Options are
                              'all', 'expired', and 'valid'.
        :returns: A list of dictionaries representing the requested SSL certs.

        Example::

            # Get all valid SSL certs
            certs = mgr.list_certs(method='valid')
            print certs

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
        """Creates a new certificate.

        :param dict certificate: A dictionary representing the parts of the
                                 certificate.
                                 See developer.softlayer.com for more info.

        Example::

            cert = ??
            result = mgr.add_certificate(certificate=cert)

        """
        return self.ssl.createObject(certificate)

    def remove_certificate(self, cert_id):
        """Removes a certificate.

        :param integer cert_id: a certificate ID to remove

        Example::

            # Removes certificate with id 1234
            result = mgr.remove_certificate(cert_id = 1234)
        """
        return self.ssl.deleteObject(id=cert_id)

    def edit_certificate(self, certificate):
        """Updates a certificate with the included options.

        The provided dict must include an 'id' key and value corresponding to
        the certificate ID that should be updated.

        :param dict certificate: the certificate to update.

        Example::

            # Updates the cert id 1234
            cert['id'] = 1234
            cert['certificate'] = ??
            result = mgr.edit_certificate(certificate=cert)

        """
        return self.ssl.editObject(certificate, id=certificate['id'])

    def get_certificate(self, cert_id):
        """Gets a certificate with the ID specified.

        :param integer cert_id: the certificate ID to retrieve

        Example::

            cert = mgr.get_certificate(cert_id=1234)
            print(cert)

        """
        return self.ssl.getObject(id=cert_id)
