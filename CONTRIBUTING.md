# Contributing to softlayer-python

We are happy to accept contributions to softlayer-python.  Please follow the
guidelines below.  

## Procedural

1. All code changes require a corresponding issue. [Open an issue here](https://github.com/softlayer/softlayer-python/issues). 
2. Fork the [softlayer-python](https://github.com/softlayer/softlayer-python) repository.
3. Make any changes required, commit messages should reference the issue number (include #1234 if the message if your issue is number 1234 for example).
4. Make a pull request from your fork/branch to origin/master
5. Requires 1 approval for merging

* Additional infomration can be found in our [contribution guide](http://softlayer-python.readthedocs.org/en/latest/dev/index.html)

## Legal

* See our [Contributor License Agreement](./docs/dev/cla-individual.md). Opening a pull request is acceptance of this agreement.

* If you're contributing on behalf of your employer we'll need a signed copy of our corporate contributor agreement (CCLA) as well.  You can find the [CCLA here](./docs/dev/cla-corporate.md).


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


## Project Management

### Issues

* ~~Title~~: Should contain quick highlight of the issue is about
* ~~Body~~: All the technical information goes here
* ~~Assignee~~: Should be the person who is actively working on an issue.
* ~~Label~~: All issues should have at least 1 Label.
* ~~Projects~~: Should be added to the quarerly Softlayer project when being worked on
* ~~Milestones~~: Not really used, can be left blank
* ~~Linked Pull Request~~: Should be linked to the relavent pull request when it is opened.

### Pull Requests

* ~~Title~~: Should be similar to the title of the issue it is fixing, or otherwise descibe what is chaning in the pull request
* ~~Body~~: Should have "Fixes #1234" at least, with some notes about the specific pull request if needed. Most technical information should still be in the github issue.
* ~~Reviewers~~: 1 Reviewer is required
* ~~Assignee~~: Should be the person who opened the pull request
* ~~Labels~~: Should match the issue
* ~~Projects~~: Should match the issue
* ~~Milestones~~: Not really used, can be left blank
* ~~Linked issues~~: If you put "Fixes #<Issue number>" in the body, this should be automatically filled in, otherwise link manually.

### Code Reviews
All issues should be reviewed by at least 1 member of the SLDN team that is not the person opening the pull request. Time permitting, all members of the SLDN team should review the request.

#### Things to look for while doing a review

As a reviewer, these are some guidelines when doing a review, but not hard rules. 

* Code Style: Generally `tox -e analysis` will pick up most style violations, but anything that is wildly different from the normal code patters in this project should be changed to match, unless there is a strong reason to not do so.
* API Calls: Close attention should be made to any new API calls, to make sure they will work as expected, and errors are handled if needed.
* DocBlock comments: CLI and manager methods need to be documented well enough for users to easily understand what they do.
* Easy to read code: Code should generally be easy enough to understand at a glance. Confusing code is a sign that it should either be better documented, or refactored a bit to be clearer in design.


### Testing

When doing testing of a code change, indicate this with a comment on the pull request like 

:heavy_check: `slcli vs list --new-feature` 
:x: `slcli vs list --broken-feature`
