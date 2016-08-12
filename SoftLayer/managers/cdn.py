"""
    SoftLayer.cdn
    ~~~~~~~~~~~~~
    CDN Manager/helpers

    :license: MIT, see LICENSE for more details.
"""
import six

from SoftLayer import utils


MAX_URLS_PER_LOAD = 5
MAX_URLS_PER_PURGE = 5


class CDNManager(utils.IdentifierMixin, object):
    """Manage CDN accounts."""

    def __init__(self, client):
        self.client = client
        self.account = self.client['Network_ContentDelivery_Account']

    def list_accounts(self):
        """Lists CDN accounts for the active user."""

        account = self.client['Account']
        mask = 'cdnAccounts[%s]' % ', '.join(['id',
                                              'createDate',
                                              'cdnAccountName',
                                              'cdnSolutionName',
                                              'cdnAccountNote',
                                              'status'])
        return account.getObject(mask=mask).get('cdnAccounts', [])

    def get_account(self, account_id, **kwargs):
        """Retrieves a CDN account with the specified account ID.

        :param account_id int: the numeric ID associated with the CDN account.
        :param dict \\*\\*kwargs: additional arguments to include in the object
                                mask.
        """

        if 'mask' not in kwargs:
            kwargs['mask'] = 'status'

        return self.account.getObject(id=account_id, **kwargs)

    def get_origins(self, account_id, **kwargs):
        """Retrieves list of origin pull mappings for a specified CDN account.

        :param account_id int: the numeric ID associated with the CDN account.
        :param dict \\*\\*kwargs: additional arguments to include in the object
                                mask.
        """

        return self.account.getOriginPullMappingInformation(id=account_id,
                                                            **kwargs)

    def add_origin(self, account_id, media_type, origin_url, cname=None,
                   secure=False):
        """Adds an original pull mapping to an origin-pull.

        :param int account_id: the numeric ID associated with the CDN account.
        :param string media_type: the media type/protocol associated with this
                                  origin pull mapping; valid values are HTTP,
                                  FLASH, and WM.
        :param string origin_url: the base URL from which content should be
                                  pulled.
        :param string cname: an optional CNAME that should be associated with
                             this origin pull rule; only the hostname should be
                             included (i.e., no 'http://', directories, etc.).
        :param boolean secure: specifies whether this is an SSL origin pull
                               rule, if SSL is enabled on your account
                               (defaults to false).
        """

        config = {'mediaType': media_type,
                  'originUrl': origin_url,
                  'isSecureContent': secure}

        if cname:
            config['cname'] = cname

        return self.account.createOriginPullMapping(config, id=account_id)

    def remove_origin(self, account_id, origin_id):
        """Removes an origin pull mapping with the given origin pull ID.

        :param int account_id: the CDN account ID from which the mapping should
                               be deleted.
        :param int origin_id: the origin pull mapping ID to delete.
        """

        return self.account.deleteOriginPullRule(origin_id, id=account_id)

    def load_content(self, account_id, urls):
        """Prefetches one or more URLs to the CDN edge nodes.

        :param int account_id: the CDN account ID into which content should be
                               preloaded.
        :param urls: a string or a list of strings representing the CDN URLs
                     that should be pre-loaded.
        :returns: true if all load requests were successfully submitted;
                  otherwise, returns the first error encountered.
        """

        if isinstance(urls, six.string_types):
            urls = [urls]

        for i in range(0, len(urls), MAX_URLS_PER_LOAD):
            result = self.account.loadContent(urls[i:i + MAX_URLS_PER_LOAD],
                                              id=account_id)
            if not result:
                return result

        return True

    def purge_content(self, account_id, urls):
        """Purges one or more URLs from the CDN edge nodes.

        :param int account_id: the CDN account ID from which content should
                               be purged.
        :param urls: a string or a list of strings representing the CDN URLs
                     that should be purged.
        :returns: true if all purge requests were successfully submitted;
                  otherwise, returns the first error encountered.
        """

        if isinstance(urls, six.string_types):
            urls = [urls]

        for i in range(0, len(urls), MAX_URLS_PER_PURGE):
            result = self.account.purgeCache(urls[i:i + MAX_URLS_PER_PURGE],
                                             id=account_id)
            if not result:
                return result

        return True
