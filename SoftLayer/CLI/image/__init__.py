"""Compute images."""
# :license: MIT, see LICENSE for more details.
from SoftLayer.CLI import formatting


MASK = ('id,createDate,note,accountId,name,globalIdentifier,parentId,publicFlag,flexImageFlag,'
        'imageType,children[blockDevices[diskImage[softwareReferences[softwareDescription]]]]')
DETAIL_MASK = MASK + (',firstChild,children[id,blockDevicesDiskSpaceTotal,datacenter,'
                      'transaction[transactionGroup,transactionStatus],'
                      'blockDevices[diskImage[capacity,name,units,softwareReferences[softwareDescription]],diskSpace]],'
                      'note,createDate,status,transaction,accountReferences')
PUBLIC_TYPE = formatting.FormattedItem('PUBLIC', 'Public')
PRIVATE_TYPE = formatting.FormattedItem('PRIVATE', 'Private')
