## Status

[![Build Status](https://travis-ci.org/softlayer/softlayer-python.svg?branch=gh-pages)](https://travis-ci.org/softlayer/softlayer-python?branch=gh-pages)
[![Dependency Status](https://gemnasium.com/softlayer/softlayer-python.svg?branch=gh-pages)](https://gemnasium.com/softlayer/softlayer-python)
[![MIT-license badge](http://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/softlayer/softlayer-python/blob/gh-pages/LICENSE.md)

---

## Contents

* [Introduction](#introduction)
* [Features and Plugins](#features-and-plugins)
* [Compatibility](#compatibility)
* [Prerequisites](#prerequisites)
* [Getting Started](#getting-started)
* [Code Organization](#code-organization)
* [Automation](#automation)
* [Metadata](#metadata)
* [DOM Elements](#dom-elements)
* [Color Palette](#color-palette)
* [Code Styles](#code-styles)
* [Got Problems?](#got-problems)

---

## Introduction

We use a homegrown, content-first boilerplate for GitHub docs. It provides the facilities to write content exclusively in Markdown and spin-up [Jekyll](http://jekyllrb.com)-powered static websites, as well as:

* Guaranteeing fast load times
* Automating repetitive tasks
* Rooting responsiveness and accessibility right from its core
* Providing estimated reading times
* Having indexes/table of contents built on-the-fly
* Encoding URLs with the apt labels to help users filter and create issues precisely
* Supporting native instances on Windows 7/8 OSes

<a href="#">back to top</a>

---

## Features and Plugins

Below is a list of functional and aesthetic features, baked-in components, and JS plugins.

### Core Features

* [CSS3](http://www.css3.info)
* Grids and MQs from [Bootstrap](http://twitter.github.io/bootstrap)
* [HTML5](http://www.sitepoint.com/a-basic-html5-template)
* [Node.js](http://nodejs.org)
* Pretty URLs
* [Python](http://www.python.org)
* [Repository Metadata](http://help.github.com/articles/repository-metadata-on-github-pages) for GitHub Pages
* [Ruby](http://www.ruby-lang.org/en/)
* [Sitemaps.org](http://sitemaps.org)-compliant sitemap
* [Viewports](http://github.com/h5bp/html5-boilerplate/blob/master/doc/extend.md#web-apps) for device and OS support, including iOS 7.1+

### Components

* [Font Awesome](http://fortawesome.github.io/Font-Awesome) iconic font
* [Grunt](http://gruntjs.com) task runner
* [Jekyll](http://jekyllrb.com "Jekyll") for free web hosting using GitHub Pages
* [jQuery](http://jquery.com)
* [LESS](http://lesscss.org) dynamic stylesheets for variables, mixins, nesting, and more
* [Liquid](http://liquidmarkup.org "Liquid") templating language with [logic tags](https://github.com/softlayer/softlayer-python/blob/gh-pages/_includes/handlers/items.html) for self-generating nav links
* [Modernizr](http://modernizr.com) for legacy- and cross-browser support
* [Normalize.css](http://necolas.github.io/normalize.css) for CSS normalization and resets
* [Pygments](http://pygments.org "Pygments") with a custom theme for code highlighting
* [Redcarpet](http://github.com/vmg/redcarpet "Redcarpet") for Markdown-compatibility and rendering
* [Universal Analytics](http://www.google.com/analytics) with [page scroll tracking](https://github.com/h5bp/html5-boilerplate/blob/master/doc/extend.md#google-universal-analytics) from Google

### Plugins

* [Classify](http://github.com/softlayer/softlayer-python/blob/gh-pages/plugins/classify.js) DOM utility for class helper functions
* [Indexing](http://github.com/softlayer/softlayer-python/blob/gh-pages/plugins/indexing.js) plugin for building table of contents on-the-fly
* [Portfolio](http://github.com/softlayer/softlayer-python/blob/gh-pages/plugins/portfolio.js) plugin for fetching GitHub data using AJAX and JSON
* [Readability](http://github.com/softlayer/softlayer-python/blob/gh-pages/plugins/readability.js) to make HTML5 more accessible and gauge how long it takes to read a single page
* [Scrollable](http://github.com/softlayer/softlayer-python/blob/gh-pages/plugins/scrollable.js) to apply thresholds for HTML elements while scrolling
* [Toggle](http://github.com/softlayer/softlayer-python/blob/gh-pages/plugins/toggle.js) handles the sliding and collapsing behavior for navigation

<a href="#">back to top</a>

---

## Compatibility

For the best performance and usability, we recommend the latest versions of the browsers and platforms listed below. As for legacy browsers, the Modernizr plugin does its best but it's not perfect. And like most sites today, we use JS to render on-page elements. If it's disabled in your browser, you might not see those elements.

Starting from the best to the worst, we suggest the following:

* Chrome (~100%)
* Safari (~75%)
* Firefox (~50%)
* Opera (~50%)
* Internet Explorer (~25%)

The table below is a comparison of OS platforms and browsers.

| Platform    | Chrome  | Firefox   | Internet Explorer   | Opera   | Safari          |
| ----------- | ------- | --------- | ------------------- | ------- | --------------- |
| Android     | **Yes** | No        | N/A                 | No      | N/A             |
| iOS         | **Yes** | N/A       | N/A                 | No      | **Yes**         |
| Mac OS X    | **Yes** | **Yes**   | N/A                 | **Yes** | **Yes**         |
| Windows     | **Yes** | **Yes**   | **Yes**             | **Yes** | **Yes** <sup>see note</sup>  |

> Note: Apple no longer provides updates for Safari on Windows. Due to the lack of security updates, we **do not recommend** using Safari on Windows. Use Chrome instead.

<a href="#">back to top</a>

---

## Prerequisites

Our boilerplate requires the minimum versions for Ruby, Python, and Node.js. Use the links to get download and install information for your specific OS.

* [Ruby 2.0.0](http://www.ruby-lang.org/en/installation)
* [Python 2.7.6](http://www.python.org/download) <sup>see note</sup>
* [Node.js 0.10.20](http://nodejs.org/download)

> Note: Python powers Pygments, which we use for code highlighting. Currently, Pygments 1.6 is not compatible with Python 3. **You must have Python 2 installed** until Pygments 2.0 is released (date pending).

### Windows Users

Read Yi Zeng's [Setup Jekyll on Windows](http://yizeng.me/2013/05/10/setup-jekyll-on-windows "Setup Jekyll on Windows") article before getting into the thick of things. It will save you a ton of time and agony.

<a href="#">back to top</a>

---

## Getting Started

1. Verify that __Ruby__, __Python__ and __Node.js__ are installed
    ~~~sh
    # each command returns a version number
    $ ruby -v
    $ python --version
    $ node  --version
    ~~~

2. Clone from GitHub and go into the directory (~5 sec.)

    ~~~sh
    $ git clone -b gh-pages https://github.com/softlayer/softlayer-python.git
    $ cd softlayer-python
    ~~~

3. Install Grunt (~3 sec.)

    ~~~sh
    $ [sudo] npm install -g grunt-cli
    ~~~

4. Install modules for Node.js (~15 sec.)

    ~~~sh
    $ [sudo] npm install
    ~~~

5. Install Jekyll, Pygments and other dependencies (~35 sec.)

    ~~~sh
    $ [sudo] grunt install
    ~~~

<a href="#">back to top</a>

---

## Code Organization

Below is the basic spread for our directory (not including `node_modules` for Grunt, `_site` for Jekyll, or any directories made for one-off projects).

<pre>
├─ _includes/
│   ├─ content/
│   ├─ handlers/
│   └─ partials/
├─ _layout/
├─ assets/
│   ├─ css/
│   ├─ images/
│   ├─ js/
│   └─ packages/
├─ less/
├─ plugins/

5 directories, 7 subdirectories
</pre>

### Directory

Here's an overview of what each directory does or contains.

| Directory               | Overview  |
| ----------------------- | --------- |
| <samp>_includes/</samp> | Reusable content (“partials”) and semantic HTML elements. `{% include file.ext %}` tags indicate where partials are being used. |
| <samp>_layouts/</samp>  | Reusable templates designed for specific uses, like **pages**, **news**, **articles**, and **blogs**. `{{content}}` tags inject external content into layouts. |
| <samp>assets/</samp>    | Static and transpiled resources. This includes JS, CSS, and images.|
| <samp>less/</samp>      | Source for `*.less` stylesheets. Bundled LESS files are stored in `assets/css`. |
| <samp>plugins/</samp>   | Source for `*.js` scripts. Bundled JS files are stored in `assets/js`. |

### Subdirectory

Here's an overview of each subdirectory.

| Subdirectory                    | Overview |
| ------------------------------- | -------- |
| <samp>_includes/content/</samp>  | Reusable, plain-text snippets for documentation. |
| <samp>_includes/handlers/</samp> | [Logic tags](http://docs.shopify.com/themes/liquid-basics) for the Liquid templating engine. |
| <samp>_includes/partials/</samp> | Reusable, HTML snippets for documentation and landing pages. |
| <samp>assets/css/</samp>         | Static directory for bundled CSS resources. |
| <samp>assets/images/</samp>      | Source for all images, including favicons and logos. |
| <samp>assets/js/</samp>          | Static directory for bundled JS resources. |
| <samp>assets/packages/</samp>    | Source for `ez_setup.py` and `get-pip.py`. |

<a href="#">back to top</a>

---

## Automation

We're proponents of DRY (don't repeat yourself). After all, the more automation there is, the less repetitive work you have (and hopefully the less mistakes you make).

Using [Grunt](http://gruntjs.com), we built a powerful harness that automates ankle-biters like:

* Bundling JS files and transpiling LESS into CSS
* Validating HTML markup
* Installing runtime dependencies for Ruby and Node
* Previewing work locally before pushing it to GitHub

See our list of [Grunt Tasks](#grunt-tasks) below.

### Grunt Tasks

Run any of these commands to initiate a task.

* [`grunt build`](#grunt-build)
* [`grunt install`](#grunt-install)
* [`grunt preview`](#grunt-preview)
* [`grunt serve`](#grunt-serve)
* [`grunt test`](#grunt-test)

#### Grunt Build

Run `grunt build` to perform the following:

1. Bundle and minify `*.js` files using [UglifyJS](http://lisperator.net/uglifyjs)
2. Bundle and minify `*.less` files to `*.css` using [RECESS](http://twitter.github.io/recess)

#### Grunt Install

Run `grunt install` to perform the following:

1. Install [Bundler](http://bundler.io)
2. Read in the Rubygem dependencies from the [Gemfile](gemfile)
3. Use Bundler's CLI to install the necessary gems

#### Grunt Preview

Run `grunt preview` to perform the following:

1. Build the website locally in the `_site` directory
2. Start a local environment on [http://localhost:4000](http://localhost:4000)
3. Regenerate the site whenever files are modified (except JS and LESS stylesheets)

> Preview mode lasts forever. It will not timeout after a period of non-usage. In order to kill it, press `CTRL+C`.

#### Grunt Serve

*This task is a combination of `grunt build` and `grunt preview`.*

Run `grunt serve` to perform the following:

1. Bundle and minify `*.js` files using [UglifyJS](http://lisperator.net/uglifyjs)
2. Bundle and minify `*.less` files to `*.css` using [RECESS](http://twitter.github.io/recess)
3. Build the website locally in the `_site` directory
4. Start a local environment on [http://localhost:4000](http://localhost:4000)
5. Watch and regenerate a new `_site` directory whenever a file is modified (except JS and LESS stylesheets)

> Just like with `grunt preview`, serve mode lasts forever. It will not timeout after a period of non-usage. In order to kill it, press `CTRL+C`.

#### Grunt Test

Run `grunt test` to perform the following:

1. Build the website locally in the `_site` directory
2. Test all `*html` files against [W3's HTML validation service](http://validator.w3.org)
3. Spit out logs

### Updating Grunt Dependencies

Dependencies are updated often by their original authors. To keep up with them, we test and update the version levels in `package.json`. However, dependencies do not update themselves automatically. To install the most recent versions, run the following commands to delete the original <samp>node_modules</samp> directory and build a new one.

~~~sh
$ [sudo] rm -r node_modules
$ [sudo] npm install
~~~

<a href="#">back to top</a>

---

## DOM Elements

Several DOM elements are embedded within JS and render on the home/landing page. The table below provides the name and purpose of each element (in alphabetical order).

| DOM Elements           | Purpose                                                |
| ---------------------- | ------------------------------------------------------ |
| `#github-contributors` | Total number of contributors for a single repo         |
| `#github-repos`        | Total number of repos for a single organization        |
| `#github-stargazers`   | Total number of stargazers for a single repo           |
| `#github-version`      | Version number for the last pegged released            |
| `#github-watchers`     | Total number of watchers/subscribers for a single repo |

<a href="#">back to top</a>

---

## Metadata

We harness several metadata tags using GitHub's [repository metadata](http://help.github.com/articles/repository-metadata-on-github-pages) feature, albeit not all of them for a number of reasons.

Below is a list of metadata tags we use.

| Metadata Tags                     | Example                                             |
| --------------------------------- | --------------------------------------------------- |
| `{{site.github.issues_url}}`      | http://github.com/softlayer/softlayer-python/issues |
| `{{site.github.owner_url}}`       | http://github.com/softlayer |
| `{{site.github.project_tagline}}` | "A set of Python libraries that assist in calling the SoftLayer API." |
| `{{site.github.releases_url}}`    | http://github.com/softlayer/softlayer-python/releases |
| `{{site.github.repository_url}}`  | http://github.com/softlayer/softlayer-python |
| `{{site.github.url}}`             | http://softlayer.github.io/softlayer-python |

<a href="#">back to top</a>

---

## Color Palette

The colors below correspond with their respective LESS `@xxxx` variables.

### Colors

![](http://www.placehold.it/200/3C464C/ffffff&text=@default)
![](http://www.placehold.it/200/7B807C/ffffff&text=@gray)
![](http://www.placehold.it/200/4073BD/ffffff&text=@blue)
![](http://www.placehold.it/200/DD0224/ffffff&text=@red)
![](http://www.placehold.it/200/1ABD6C/ffffff&text=@green)

### Base Colors

![](http://www.placehold.it/200/FFFFFF/999999&text=@white)
![](http://www.placehold.it/200/F8F8F8/999999&text=@base90)
![](http://www.placehold.it/200/F0F0F0/999999&text=@base80)
![](http://www.placehold.it/200/DADADA/999999&text=@base70)
![](http://www.placehold.it/200/BABABA/ffffff&text=@base60)
![](http://www.placehold.it/200/AAAAAA/ffffff&text=@base50)
![](http://www.placehold.it/200/777777/ffffff&text=@base40)
![](http://www.placehold.it/200/555555/ffffff&text=@base30)
![](http://www.placehold.it/200/333333/ffffff&text=@base20)
![](http://www.placehold.it/200/222222/ffffff&text=@base10)
![](http://www.placehold.it/200/151515/ffffff&text=@black)

<a href="#">back to top</a>

---

## Code Styles

Use the settings below to help unify coding styles across different editors.

* `indent_style = space`
* `end_of_line = lf`
* `charset = utf-8`
* `trim_trailing_whitespace = true`
* `insert_final_newline = false`
* `indent_size = 4`

Sublime Text users can configure these settings manually by opening <samp>Preferences > Settings - User</samp>, inserting the lines below, and saving your settings.

<pre>
{
  "translate_tabs_to_spaces": true,
  "tab_size": 4,
  "ensure_newline_at_eof_on_save": false,
  "default_encoding": "UTF-8",
  "default_line_ending": "lf",
  "trim_trailing_white_space_on_save": true
}
</pre>

### Sublime Packages

Sublime does not include every syntax highlight. To get certain highlights, you have to install them by hand. The instructions below delve into the install processes for __Jekyll__, __LESS__, and __Liquid__.

Use [Package Control](http://sublime.wbond.net), Sublime's built-in tool, to install these syntaxes. If you already have Package Control, skip the rest of this and click any of the links below. If you don't, this [install guide](http://sublime.wbond.net/installation) will walk you through all the install options. Once that's done, click any of these links:

* [Jekyll](#jekyll)
* [LESS](#less)
* [Liquid](#liquid)

#### Jekyll

1. Open Preferences > Package Control.
2. Type `Install Package` and hit return.
3. Type `Jekyll` and hit return.

> The Jekyll package includes syntaxes for HTML, JSON, Markdown, and Textile.

#### LESS

1. Open Preferences > Package Control.
2. Type `Install Package` and hit return.
3. Type `LESS` and hit return.

#### Liquid

1. Open Preferences > Package Control.
2. Type `Install Package` and hit return.
3. Type `Siteleaf Liquid Syntax` and hit return.

> The Liquid package includes syntax for HTML.

<a href="#">back to top</a>

---

## Got Problems?

Below are a few issues and solutions (or workarounds) that we came across during development.

#### Incompatible character encodings

If you get **Liquid Exception: incompatible character encodings: UTF-8 and IBM437...** after running `grunt serve`, this means your CLI does not use UTF-8 by default (example: Git for Windows). A workaround is to run the following commands before running `grunt serve`.

~~~sh
$ cmd
$ chcp 65001
$ exit
~~~

> Note: You only need to run these commands when you first open your CLI. The settings persist locally until you close it.

#### Conversion error

If you're getting a **Conversion error: There was an error converting *file_name.md*"** message, this means a HTML tag is not closed. To fix this, close all HTML tags.

> Tip: Run `grunt test` to help find the open tag.

#### Liquid Exception: Cannot find /bin/sh

If you're getting a **Liquid Exception: Cannot find /bin/sh**, this means you have a buggy version of `pygments.rb`. A workaround is to use `pygments.rb` version 0.5.0. This means you'll have to uninstall newer versions as well. To do this, run the following commands.

~~~sh
$ gem uninstall pygments.rb --version "=0.5.4"
$ gem uninstall pygments.rb --version "=0.5.2"
$ gem uninstall pygments.rb --version "=0.5.1"
$ gem install pygments.rb --version "=0.5.0"
~~~

#### Not Found: '/' not found

If you're getting a **'/' not found** error when you open a browser to `localhost:4000`, this means something went wrong when Jekyll created the `_site` directory. It has nothing to do with you, it's all Jekyll. To fix this, type `CTRL+C` to stop Jekyll and try again.

#### Warning: cannot close fd before spawn

If you get **Warning: cannot close fd before spawn** after running `grunt serve`, this means something went wrong when Jekyll created the `_site` directory. It has nothing to do with you, it's all Jekyll. To fix this, run `grunt serve` again.

<a href="#">back to top</a>
