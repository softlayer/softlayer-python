# Contributing to softlayer-python

We are happy to accept contributions to softlayer-python.  Please follow the
guidelines below.  

* Sign our contributor agreement (CLA) You can find the [CLA here](./docs/dev/cla-individual.md).

* If you're contributing on behalf of your employer we'll need a signed copy of our corporate contributor agreement (CCLA) as well.  You can find the [CCLA here](./docs/dev/cla-corporate.md).
    
* Fork the repo, make your changes, and open a pull request.

* Additional infomration can be found in our [contribution guide](http://softlayer-python.readthedocs.org/en/latest/dev/index.html)


## Code style

Code is tested and style checked with tox, you can run the tox tests individually by doing `tox -e <TEST>`

* `autopep8 -r  -v -i --max-line-length 119  SoftLayer/`
* `autopep8 -r  -v -i --max-line-length 119  tests/`
* `tox -e analysis`
* `tox -e py36`
* `git commit --message="#<ISSUENUMBER> <whatever you did>`
* `git push origin <issueBranch>`
* create pull request


## Documentation

CLI command should have a more human readable style of documentation.
Manager methods should have a decent docblock describing any parameters and what the method does.

Docs are generated with [Sphinx](https://docs.readthedocs.io/en/latest/intro/getting-started-with-sphinx.html) and once Sphinx is setup, you can simply do

`make html` in the softlayer-python/docs directory, which should generate the HTML in softlayer-python/docs/_build/html for testing. 


## Unit Tests

All new features should be 100% code covered, and your pull request should at the very least increase total code overage. 

### Mocks
To tests results from the API, we keep mock results in SoftLayer/fixtures/<SoftLayer_Service>/ with the method name matching the variable name.

Any call to a service that doesn't have a fixture will result in a TransportError

### Overriding Fixtures

Adding your expected output in the fixtures file with a unique name is a good way to define a fixture that gets used frequently in a test.

```python
from SoftLayer.fixtures import SoftLayer_Product_Package
    
    def test_test(self):
        amock = self.set_mock('SoftLayer_Product_Package', 'getAllObjects')
        amock.return_value = fixtures.SoftLayer_Product_Package.RESERVED_CAPACITY
```

Otherwise defining it on the spot works too.
```python
    def test_test(self):
        mock = self.set_mock('SoftLayer_Network_Storage', 'getObject')
        mock.return_value = {
            'billingItem': {'hourlyFlag': True, 'id': 449},
        }
```


### Call testing
Testing your code to make sure it makes the correct API call is also very important.

The testing.TestCase class has a method call `assert_called_with` which is pretty handy here.

```python
self.assert_called_with(
    'SoftLayer_Billing_Item', # Service
    'cancelItem',             # Method
    args=(True, True, ''),    # Args
    identifier=449,           # Id
    mask=mock.ANY,            # object Mask,
    filter=mock.ANY,          # object Filter
    limit=0,                  # result Limit
    offset=0                  # result Offset 
)
```

Making sure a API was NOT called

```python
self.assertEqual([], self.calls('SoftLayer_Account', 'getObject'))
```

Making sure an API call has a specific arg, but you don't want to list out the entire API call (like with a place order test)

```python
# Get the API Call signature
order_call = self.calls('SoftLayer_Product_Order', 'placeOrder')

# Get the args property of that API call, which is a tuple, with the first entry being our data.
order_args = getattr(order_call[0], 'args')[0]

# Test our specific argument value
self.assertEqual(123, order_args['hostId'])
```