getUnattachedTagsForCurrentUser = [{'id': 287895, 'name': 'coreos', 'referenceCount': 0}]
getAttachedTagsForCurrentUser = [{'id': 1286571, 'name': 'bs_test_instance', 'referenceCount': 5}]
getReferences = [
    {
        'id': 73009305,
        'resourceTableId': 33488921,
        'tag': {
            'id': 1286571,
            'name': 'bs_test_instance',
        },
        'tagId': 1286571,
        'tagType': {'description': 'CCI', 'keyName': 'GUEST'},
        'tagTypeId': 2,
        'usrRecordId': 6625205
    }
]

deleteTag = True

setTags = True

getObject = getAttachedTagsForCurrentUser[0]

getTagByTagName = getAttachedTagsForCurrentUser

getAllTagTypes = [
    {
        "description": "Hardware",
        "keyName": "HARDWARE"
    }
]
