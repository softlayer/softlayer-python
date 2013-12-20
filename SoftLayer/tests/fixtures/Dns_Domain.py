createObject = {'name': 'example.com'}
deleteObject = True
editObject = True
getZoneFileContents = 'lots of text'
getResourceRecords = [
    {'ttl': 7200, 'data': 'd', 'host': 'a', 'type': 'cname'},
    {'ttl': 900, 'data': '1', 'host': 'b', 'type': 'a'},
    {'ttl': 900, 'data': 'x', 'host': 'c', 'type': 'ptr'},
    {'ttl': 86400, 'data': 'b', 'host': 'd', 'type': 'txt'},
    {'ttl': 86400, 'data': 'b', 'host': 'e', 'type': 'txt'},
    {'ttl': 600, 'data': 'b', 'host': 'f', 'type': 'txt'},
]
getObject = {'id': 98765, 'name': 'test-example.com'}
