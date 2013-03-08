__all__ = ['CDNManager']


class CDNManager(object):
    def __init__(self, client):
        self.client = client
        self.account = self.client['Network_ContentDelivery_Account']

    def list_accounts(self):
        account = self.client['Account']
        mask = 'cdnAccounts[%s]' % ', '.join(['id',
                                              'cdnAccountName',
                                              'cdnSolutionName',
                                              'cdnAccountNote',
                                              'status'])
        return account.getObject(mask=mask).get('cdnAccounts', [])
