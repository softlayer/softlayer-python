"""Compute images."""
# :license: MIT, see LICENSE for more details.
from SoftLayer.CLI import formatting


MASK = ('id,accountId,name,globalIdentifier,parentId,publicFlag,flexImageFlag,'
        'imageType')
DETAIL_MASK = MASK + (',firstChild,children[id,blockDevicesDiskSpaceTotal,datacenter,'
                      'transaction[transactionGroup,transactionStatus]],'
                      'note,createDate,status,transaction')
PUBLIC_TYPE = formatting.FormattedItem('PUBLIC', 'Public')
PRIVATE_TYPE = formatting.FormattedItem('PRIVATE', 'Private')
