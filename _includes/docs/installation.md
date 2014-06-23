## Quick Install

These options will download and install packages automatically.

* [Pip](#toc_4)
* [Pip from GitHub](#toc_5)
* [Debian/Ubuntu](#toc_6)

### Pip

Run the command below to use <a href="https://pypi.python.org/pypi/pip" target="_blank">pip</a>.

```bash
$ pip install softlayer
```

### Pip from GitHub

Run the command below to pull the {{site.project.alias}} down from GitHub and install it using pip (requires [Git](#toc_1)).

```bash
$ pip install git+git://github.com/softlayer/softlayer-python.git
```

### Debian/Ubuntu

For Debian <a href="https://www.debian.org/releases/jessie" target="_blank">“jessie”</a> (in testing) and Ubuntu 14.04, run the command below to install our official packages.

```bash
$ sudo apt-get install python-softlayer
```

***
## Not-So Quick Install

Without `pip` or Debian/Ubuntu, you'll need to do things manually. This includes:

1. Installing [Git](#toc_1) (if you haven't already)
2. Downloading or cloning the {{site.project.alias}} from GitHub
3. [Installing the {{site.project.alias}}](#toc_12) into your site-packages

Scroll through the following download and clone options and pick one that works best for you.

* [Tarball Download](#toc_8)
* [Zipball Download](#toc_9)
* [HTTPS Clone](#toc_10)
* [SSH Clone](#toc_11)

### Tarball Download

<a href="{{site.github.download.tarball}}">Download here <i class="fa fa-cloud-download"></i></a> or run the command below.

```bash
$ curl -OL {{site.github.download.tarball}}
```

### Zipball Download

<a href="{{site.github.download.zipball}}">Download here <i class="fa fa-cloud-download"></i></a> or run the command below.

```bash
$ curl -OL {{site.github.download.zipball}}
```

### HTTPS Clone

Run the command below to clone over HTTPS.

```bash
$ git clone {{site.github.clone.https}}
```

### SSH Clone

Run the command below to clone over SSH.

```bash
$ git clone {{site.github.clone.ssh}}
```

### Install into Site Packages

Once you have a copy of the {{site.project.alias}}, install it into your site-packages by running the following command.

```bash
$ python setup.py install
```
