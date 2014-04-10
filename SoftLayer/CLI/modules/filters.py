"""
usage: sl help filters

Filters are used to limit the amount of results. Some commands will accept a
filter operation for certain fields. Filters can be applied across multiple
fields in most cases.

Available Operations:
  Case Insensitive
    'value'   Exact value match
    'value*'  Begins with value
    '*value'  Ends with value
    '*value*' Contains value

  Case Sensitive
    '~ value'   Exact value match
    '> value'   Greater than value
    '< value'   Less than value
    '>= value'  Greater than or equal to value
    '<= value'  Less than or equal to value

Examples:
    sl server list --datacenter=dal05
    sl server list --hostname='prod*'
    sl vs list --network=100 --cpu=2
    sl vs list --network='< 100' --cpu=2
    sl vs list --memory='>= 2048'

Note: Comparison operators (>, <, >=, <=) can be used with integers, floats,
      and strings.
"""
# :license: MIT, see LICENSE for more details.
