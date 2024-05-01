This document is for internal users wanting to use this library to interact with the internal API. It will not work for `api.softlayer.com`.

## SSL: CERTIFICATE_VERIFY_FAILED fix
You need to specify the server certificate to verify the connection to the internal API since its a self signed certificate. Python's request module doesn't use the system SSL cert for some reason, so even if you can use `curl` without SSL errors becuase you installed the certificate on your system, you still need to tell python about it. Further reading: 
	- https://hackernoon.com/solving-the-dreadful-certificate-issues-in-python-requests-module
	- https://levelup.gitconnected.com/using-custom-ca-in-python-here-is-the-how-to-for-k8s-implementations-c450451b6019

On Mac, after installing the softlayer.local certificate, the following worked for me:

```bash
security export -t certs -f pemseq -k /System/Library/Keychains/SystemRootCertificates.keychain -o bundleCA.pem
sudo cp bundleCA.pem /etc/ssl/certs/bundleCA.pem
```
Then in the `~/.softlayer` config, set `verify = /etc/ssl/certs/bundleCA.pem` and that should work.


## Certificate Example

For use with a utility certificate. In your config file (usually `~/.softlayer`), you need to set the following:

```
[softlayer]
endpoint_url = https://<internal api endpoint>/v3/internal/rest/
timeout = 0
theme = dark
auth_cert = /etc/ssl/certs/my_utility_cert-dev.pem
verify = /etc/ssl/certs/allCAbundle.pem
```

`auth_cert`: is your utility user certificate
`server_cert`: is the CA certificate bundle to validate the internal API ssl chain. Otherwise you get self-signed ssl errors without this.


```python
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

To login with your employee username, have your config look something like this

*NOTE*: Currently logging in with the rest endpoint doesn't quite work, so use xmlrpc until I fix [this issue](https://github.ibm.com/SoftLayer/internal-softlayer-cli/issues/10)

```
[softlayer]
username = <softlayer domain username>
endpoint_url = https://<internal api endpoint>/v3/internal/xmlrpc/
verify = /etc/ssl/certs/allCAbundle.pem
```

You can login and use the `slcli` with. Use the `-i` flag to make internal API calls, otherwise it will make SLDN api calls.

```bash
slcli -i emplogin
```

If you want to use any of the built in commands, you may need to use the `-a <accountId>` flag.