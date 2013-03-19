"""
usage: sl help filters

Filters are used to limit the amount of results. Some commands will except a
filter operation for certain fields.

Available Operations:
  'value' exact value match
  '> value' greater than value
  '< value' less than value
  '>= value' greater than or equal to value
  '<= value' less than or equal to value
  'value*' begins with value
  '*value' ends with value
  '*value*' contains value

Examples:
    sl cci list --hostname='prod.*'
    sl cci list --datacenter=dal05
    sl cci list --network=100 --cpu=2
    sl cci list --memory='>= 2048'
    sl cci list --tags=production,db

"""
# :copyright: (c) 2013, SoftLayer Technologies, Inc. All rights reserved.
# :license: BSD, see LICENSE for more details.
