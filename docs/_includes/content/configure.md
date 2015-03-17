# Configuration

You can configure the CLI easily with the **Automated Configuration Tool**. To get started, run `sl config setup`.

The setup will prompt for:

* Your SoftLayer Portal username
* Your API key
* An endpoint URL

Before you start mining for these, there are a few things you should know.

* The default endpoint will be sufficient in most cases
* You can <a href="http://knowledgelayer.softlayer.com/procedure/retrieve-your-api-key" target="_blank">create/retrieve an API key</a> from our Portal
* If you don't have an API key, use your SoftLayer Portal username instead---the CLI will generate an API key for you

<section class="panel example">
```bash
$ sl config setup

Username []: foo
API Key or Password []: bar
Endpoint (public|private|custom): public

:..............:........................................................:
:         Name : Value                                                  :
:..............:........................................................:
:     Username : foo                                                    :
:      API Key : bar                                                    :
: Endpoint URL : https://api.softlayer.com/xmlrpc/v3/                   :
:      Timeout : not set                                                :
:..............:........................................................:

Are you sure you want to write settings to "/Users/foo/.softlayer"? [Y/n]: y
Configuration Updated Successfully
```
</section>

Check your configuration by running `sl config show`.

<section class="panel example">
```bash
$ sl config show

:..............:........................................................:
:         Name : Value                                                  :
:..............:........................................................:
:     Username : foo                                                    :
:      API Key : bar                                                    :
: Endpoint URL : https://api.softlayer.com/xmlrpc/v3/                   :
:..............:........................................................:
```
</section>

> Learn how to make your own [configuration file in the Developer's Guide]({{page.baseurl}}developers-guide/#toc_21).
