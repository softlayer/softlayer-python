createObject = {'name': 'example.com'}
deleteObject = True
editObject = True
getZoneFileContents = 'lots of text'
getResourceRecords = [
    {'id': 1, 'ttl': 7200, 'data': 'd', 'host': 'a', 'type': 'cname'},
    {'id': 2, 'ttl': 900, 'data': '1', 'host': 'b', 'type': 'a'},
    {'id': 3, 'ttl': 900, 'data': 'x', 'host': 'c', 'type': 'ptr'},
    {'id': 4, 'ttl': 86400, 'data': 'b', 'host': 'd', 'type': 'txt'},
    {'id': 5, 'ttl': 86400, 'data': 'b', 'host': 'e', 'type': 'txt'},
    {'id': 6, 'ttl': 600, 'data': 'b', 'host': 'f', 'type': 'txt'},
]
getObject = {'id': 98765, 'name': 'test-example.com'}
