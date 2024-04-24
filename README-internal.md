This document is for internal users wanting to use this library to interact with the internal API. It will not work for `api.softlayer.com`.


## Certificate Example

For use with a utility certificate. In your config file (usually `~/.softlayer`), you need to set the following:

```
[softlayer]
endpoint_url = https://<internal api endpoint>/v3/internal/rest/
timeout = 0
theme = dark
auth_cert = /etc/ssl/certs/my_utility_cert-dev.pem
server_cert = /etc/ssl/certs/allCAbundle.pem
```

`auth_cert`: is your utility user certificate
`server_cert`: is the CA certificate bundle to validate the internal API ssl chain. Otherwise you get self-signed ssl errors without this.


```
import SoftLayer
import logging
import click

@click.command()
def testAuthentication():
	client = SoftLayer.CertificateClient()
	result = client.call('SoftLayer_Account', 'getObject', id=12345, mask="mask[id,companyName]")
	print(result)


if __name__ == "__main__":
	logger = logging.getLogger()
	logger.addHandler(logging.StreamHandler())
	logger.setLevel(logging.DEBUG)
	testAuthentication()
```

## Employee Example