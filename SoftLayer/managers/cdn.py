"""
    SoftLayer.managers.cdn
    ~~~~~~~~~~~~~~~~~~~~~~
    CDN Manager/helpers

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer.utils import IdentifierMixin


MAX_URLS_PER_LOAD = 5
MAX_URLS_PER_PURGE = 5


class CDNManager(IdentifierMixin, object):
    """ Manage CCIs """

    def __init__(self, client):
        self.client = client
        self.account = self.client['Network_ContentDelivery_Account']

    def list_accounts(self):
        account = self.client['Account']
        mask = 'cdnAccounts[%s]' % ', '.join(['id',
                                              'createDate',
                                              'cdnAccountName',
                                              'cdnSolutionName',
                                              'cdnAccountNote',
                                              'status'])
        return account.getObject(mask=mask).get('cdnAccounts', [])

    def get_account(self, account_id, **kwargs):
        if 'mask' not in kwargs:
            items = set(['status'])
            kwargs['mask'] = 'mask[%s]' % ','.join(items)

        return self.account.getObject(id=account_id, **kwargs)

    def get_origins(self, account_id, **kwargs):
        return self.account.getOriginPullMappingInformation(id=account_id,
                                                            **kwargs)

    def add_origin(self, account_id, media_type, origin_url, cname=None,
                   secure=False):
        config = {'mediaType': media_type,
                  'originUrl': origin_url,
                  'isSecureContent': secure}

        if cname:
            config['cname'] = cname

        return self.account.createOriginPullMapping(config, id=account_id)

    def remove_origin(self, account_id, origin_id):
        return self.account.deleteOriginPullRule(origin_id, id=account_id)

    def load_content(self, account_id, urls):
        if isinstance(urls, basestring):
            urls = [urls]

        for i in range(0, len(urls), MAX_URLS_PER_LOAD):
            result = self.account.loadContent(urls[i:i + MAX_URLS_PER_LOAD],
                                              id=account_id)
            if not result:
                return result

        return True

    def purge_content(self, account_id, urls):
        if isinstance(urls, basestring):
            urls = [urls]

        for i in range(0, len(urls), MAX_URLS_PER_PURGE):
            result = self.account.purgeContent(urls[i:i + MAX_URLS_PER_PURGE],
                                               id=account_id)
            if not result:
                return result

        return True
