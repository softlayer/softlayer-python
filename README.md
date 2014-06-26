## Contents

* [GitHub Pages](#github-pages)
* [Features and Functionality](#features-and-functionality)
* [Recommended Browsers](#recommended-browsers)
* [Prerequisites](#prerequisites)
* [Getting Started](#getting-started)
* [Grunt](#grunt)
* [Directory Structure](#directory-structure)
* [HTML DOM Elements in JS](#html-dom-elements-in-js)
* [Repository Metadata](#repository-metadata)
* [Code Styles](#code-styles)
* [Running into Problems?](#running-into-problems?)

---

## GitHub Pages

We use a homegrown, content-first framework for our GitHub docs. It provides the facilities to write content exclusively in Markdown and spin-up Jekyll-powered static websites, in addition to:

* Improving load times
* Automating repetitive tasks
* Embedding responsiveness in its core rather than wrapping code around elements
* Having indexes/table of contents built automatically
* Deploying minified or unminified JS and CSS in production
* Encoding URLs with the appropriate labels to help users filter or create issues accurately on GitHub
* Supporting local instances on Windows 7/8 OSes

---

## Features and Functionality

Below is a list of functional and aesthetic features and their purpose.

### Core Features

* Base HTML5
* [Jekyll](http://jekyllrb.com "Jekyll") for free web hosting using GitHub Pages
* [Redcarpet](http://github.com/vmg/redcarpet "Redcarpet") for Markdown-compatibility and rendering
* [Pygments](http://pygments.org "Pygments") with the [GitHub](http://richleland.github.io/pygments-css) theme for code highlighting
* [Normalize](http://necolas.github.io/normalize.css) for CSS normalization and resets
* [Liquid](http://liquidmarkup.org "Liquid") as the core templating language
* [Metadata](http://help.github.com/articles/repository-metadata-on-github-pages) for GitHub Pages
* Responsive grids and media queries from [Bootstrap](http://twitter.github.io/bootstrap)
* [Logic tags](https://github.com/softlayer/softlayer-python/blob/gh-pages/_includes/handlers/items.html) for self-generating navigation links
* Pretty URLs
* [Web-App Viewports](http://github.com/h5bp/html5-boilerplate/blob/master/doc/extend.md#web-apps) for multi-device and OS support, including iOS 7.1+
* [Sitemaps.org](http://sitemaps.org)-compliant sitemap

### Components

* [jQuery](http://jquery.com)
* [Font Awesome](http://fortawesome.github.io/Font-Awesome) iconic font
* [Grunt](http://gruntjs.com) to automate repetitive tasks
* [LESS](http://lesscss.org) dynamic stylesheets for variables, mixins, nesting, and more
* [Modernizr](http://modernizr.com) for legacy- and cross-browser support
* [Universal Analytics](http://www.google.com/analytics) snippet with [page scroll tracking](https://github.com/h5bp/html5-boilerplate/blob/master/doc/extend.md#google-universal-analytics) from Google

### Plugins

* [Classify](http://github.com/softlayer/softlayer-python/blob/gh-pages/javascript/classify.js) extensible DOM utility for class helper functions
* [Duration](http://github.com/softlayer/softlayer-python/blob/gh-pages/javascript/duration.js) to estimate how long it takes to read a single page
* [Easing](http://github.com/softlayer/softlayer-python/blob/gh-pages/javascript/easing.js) for animated page scrolling
* [Indexing](http://github.com/softlayer/softlayer-python/blob/gh-pages/javascript/indexing.js) plugin for building table of contents on-the-fly
* [Profile](http://github.com/softlayer/softlayer-python/blob/gh-pages/javascript/profiler.js) plugin for fetching organization and repository data from GitHub
* [Scrollability](http://github.com/softlayer/softlayer-python/blob/gh-pages/javascript/scrollability.js) to set thresholds for elements while scrolling
* [Toggle](http://github.com/softlayer/softlayer-python/blob/gh-pages/javascript/toggle.js) to handle sliding and collapsing behavior for navigation

---

## Recommended Browsers

We recommend the latest versions of the browsers and platforms below for the best performance and readability. For legacy browsers, the Modernizr plugin does its best but it's not perfect. Additionally, we use JS to render on-page elements. If it's disabled in your browser, you might not see those elements.

Starting from the best to the worst, we suggest the following:

* Chrome (100%)
* Safari (75%)
* Firefox (50%)
* Opera (50%)
* Internet Explorer (25%)

See the table below for a comparison of OS platforms and browsers.

| Platform    | Chrome  | Firefox | Internet Explorer | Opera   | Safari  |
| ----------- | ------- | ------- | ----------------- | ------- | ------- |
| Android     | **Yes** | No	  | N/A	              | No      | N/A     |
| iOS	      | **Yes** | N/A	  | N/A               | No      | **Yes** |
| Mac OS X    | **Yes** | **Yes** | N/A               | **Yes** | **Yes** |
| Windows     | **Yes** | **Yes** | **Yes**   	      | **Yes** | **Yes** (note) |

> Note: Apple no longer provides updates for Safari on Windows. Due to the lack of security updates, we do not recommend using Safari on Windows.

---

## Prerequisites

Our framework requires the minimum versions for Ruby, Python, and Node.js. Click the links to get download and installation information for your OS.

* [Ruby 2.0.0](http://www.ruby-lang.org/en/installation)
* [Python 2.7.5](http://www.python.org/download) (see note)
* [Node.js 0.10.20](http://nodejs.org/download)

> Note: Python powers the standard code highlighter, Pygments. Currently, Pygments 1.6 is not compatible with Python 3. **You must have Python 2 installed** until Pygments 2.0 is released (date pending).

#### Windows Users

Read Yi Zeng's [Setup Jekyll on Windows](http://yizeng.me/2013/05/10/setup-jekyll-on-windows "Setup Jekyll on Windows") article before getting into the thick of things. It will save you a ton of time and agony.

---

## Getting Started

1. Verify __Ruby__, __Python__ and __Node.js__ are installed (see [Prerequisites](#prerequisites) for supported versions)

        # each command returns a version number
        ruby -v
        python --version
        node  --version

2. Clone from GitHub

        git clone -b gh-pages https://github.com/softlayer/softlayer-python.git

3. Go into the directory

        cd softlayer-python

4. Install Grunt (takes ~3 sec.)

        [sudo] npm install -g grunt-cli

5. Install Node.js modules (takes ~15 sec.)

        [sudo] npm install

5. Install Jekyll, Pygments and other dependencies (takes ~40 sec.)

        [sudo] grunt install

---

## Grunt

We're big proponents of DRY (don't repeat yourself). That's why automation became such an important competency for this project. After all, the more automation there is, the less repetitive work you have (and hopefully the less mistakes you make).

With [Grunt](http://gruntjs.com), we're able to build a powerful harness that automates ankle-biting tasks like:

* Concatenating JS files and transpiling LESS into CSS
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
* [`grunt update`](#grunt-update)

#### Grunt Build

Run `grunt build` to perform the following:

1. Concat and minify `*.js` files using [UglifyJS](http://lisperator.net/uglifyjs)
2. Concat and minify `*.less` files to `*.css` using [RECESS](http://twitter.github.io/recess)

#### Grunt Install

Run `grunt install` to perform the following:

1. Install [Bundler](http://bundler.io)
2. Read in the Rubygem dependencies from the [Gemfile](gemfile)
3. Use Bundler's CLI to install the necessary gems

#### grunt preview

Run `grunt preview` to perform the following:

1. Build the website locally in the `_site` directory
2. Start a local environment on [http://localhost:4000](http://localhost:4000)
3. Regenerate the site whenever files are modified (except JS and LESS stylesheets)

> Preview mode lasts forever. It will not timeout after a period of non-usage. In order to kill it, press `CTRL+C`.

#### grunt serve

*This task is a combination of `grunt build` and `grunt preview`.*

Run `grunt serve` to perform the following:

1. Concat and minify `*.js` files using [UglifyJS](http://lisperator.net/uglifyjs)
2. Concat and minify `*.less` files to `*.css` using [RECESS](http://twitter.github.io/recess)
3. Build the website locally in the `_site` directory
4. Start a local environment on [http://localhost:4000](http://localhost:4000)
5. Watch and regenerate a new `_site` directory whenever a file is modified (except JS and LESS stylesheets)

> Just like with `grunt preview`, serve mode lasts forever. It will not timeout after a period of non-usage. In order to kill it, press `CTRL+C`.

#### grunt test

Run `grunt test` to perform the following:

1. Build the website locally in the `_site` directory
2. Test all `*html` files against [W3's HTML validation service](http://validator.w3.org)
3. Spit out logs

#### grunt update

Run `grunt update` to perform the following:

1. Deletes the current `node_modules` directory
2. Read in the dev dependencies from [package.json](package.json)
3. Fire off the `npm install` command
4. Install a new `node_modules` directory with the latest dev dependency versions

### Types of Grunt Tasks

This section describes the different types of Grunt tasks.

#### Alias Tasks

The tasks listed above are called "Alias" tasks. They're designed specifically for this framework and perform two or more high-level functions.

1. Reading in configuration data from package.json, config.yml, or OS environment variables
2. Generating metadata dynamically
3. Globbing multiple dependencies/plugins
4. Creating files based on different options, sources, and destinations

This table shows which dependencies each Alias task uses.

| Task    | Grunt Command   | Dev Dependencies |
| ------- | --------------- | ------------ |
| Build   | `grunt build`   | clean, concat, uglify, recess |
| Install | `grunt install` | shell |
| Preview | `grunt preview` | jekyll |
| Serve   | `grunt serve`   | clean, concat, uglify, recess, jekyll |
| Test    | `grunt test`    | jekyll, validation |
| Update  | `grunt update`  | shell |

> Dependencies are updated often by their original authors. To keep up with them, we test and update the version levels in `package.json`. However, dependencies do not update themselves automatically. To get the latest versions, run `grunt update`.

#### Basic Tasks

Unlike Alias, Basic tasks perform a much smaller set of instructions. Only a few are actually useful outside of its Alias. Those that are useful are listed below.

| Grunt Command           | Description |
| ----------------------- | ----------- |
| `grunt jekyll:preview`  | Same as the Alias `grunt preview` task |
| `grunt recess:unminify` | Concats LESS files and drops a new CSS file into `public/css/` |
| `grunt recess:minify`   | Concats and minifies LESS files and drops a new CSS file into `public/css/` |
| `grunt shell:bundler`   | Same as the Alias `grunt install` task |
| `grunt shell:npm`       | Same as the Alias `grunt update` task |
| `grunt shell:pygments`  | Installs Python setuptools, pip, and Pygments |

---

## Directory Structure

Below is the basic directory structure---not including `node_modules` (Grunt), `_site` (Jekyll), or any directories made for one-off projects.

<pre>
├─ _includes/
│  ├─ docs/
│  ├─ featured/
│  ├─ handlers/
│  └─ packages/
├─ _layout/
├─ extensions/
├─ less/
├─ public/
│  ├─ css/
│  ├─ images/
│  └─ js/

5 directories, 7 subdirectories
</pre>

### Directory

Here's an overview of what each directory does or contains.

| Directory                | Overview  |
| ------------------------ | --------- |
| <samp>_includes/</samp>  | Reusable chunks of content (called “partials”) and semantic elements. The `{% include file.ext %}` tag indicates a partial is being used. |
| <samp>_layouts/</samp>   | Reusable templates designed for specific uses, like **pages**, **news**, **articles**, and **blogs**. The `{{content}}` tag injects external content into layouts. |
| <samp>extensions/</samp> | The source for `*.js` scripts. Concatenated JS files are stored in `public/js`. |
| <samp>less/</samp>       | The source for `*.less` stylesheets. Concatenated LESS files are stored in `public/css`. |
| <samp>public/</samp>     | Static and transpiled resources used exclusively by the website. This includes JS, CSS, and images.|

### Subdirectory

Here's an overview of each subdirectory.

| Subdirectory                    | Overview |
| ------------------------------- | -------- |
| <samp>_includes/docs</samp>     | Reusable, plain-text snippets for documentation |
| <samp>_includes/featured</samp> | Reusable, HTML snippets for the landing/home page
| <samp>_includes/handlers</samp> | [Logic tags](http://docs.shopify.com/themes/liquid-basics) for the Liquid templating engine |
| <samp>_includes/packages</samp> | The source for `ez_setup.py` and `get-pip.py` |
| <samp>public/css</samp>         | Directory for static CSS resources |
| <samp>public/images</samp>      | The source for all images, including favicons and logos |
| <samp>public/js</samp>          | Directory for concatenated JS resources |

---

## HTML DOM Elements in JS

Several DOM elements are embedded within JS and render on the home/landing page. The table below provides the name and purpose of each element (in alphabetical order).

| DOM Elements           | Purpose                                                |
| ---------------------- | ------------------------------------------------------ |
| `#github-contributors` | Total number of contributors for a single repo         |
| `#github-repos`        | Total number of repos for a single organization        |
| `#github-stargazers`   | Total number of stargazers for a single repo           |
| `#github-version`      | Version number for the last pegged released            |
| `#github-watchers`     | Total number of watchers/subscribers for a single repo |

---

## Repository Metadata

We harness a few metadata tags using GitHub's [repository metadata](http://help.github.com/articles/repository-metadata-on-github-pages) feature, albeit not all of them for a number of reasons.

Below is a list of the metadata tags we use.

| Metadata Tags                     | Example                                             |
| --------------------------------- | --------------------------------------------------- |
| `{{site.github.issues_url}}`      | http://github.com/softlayer/softlayer-python/issues |
| `{{site.github.owner_url}}`       | http://github.com/softlayer |
| `{{site.github.project_tagline}}` | "A set of Python libraries that assist in calling the SoftLayer API." |
| `{{site.github.releases_url}}`    | http://github.com/softlayer/softlayer-python/releases |
| `{{site.github.repository_url}}`  | http://github.com/softlayer/softlayer-python |
| `{{site.github.url}}`             | http://softlayer.github.io/softlayer-python |

---

## Code Styles

Use the settings below to help unify coding styles for different editors.

* `indent_style = space`
* `end_of_line = lf`
* `charset = utf-8`
* `trim_trailing_whitespace = true`
* `insert_final_newline = true`
* `indent_size = 2`

Sublime Text users can configure these settings manually by opening <samp>Preferences > Settings - User</samp>, inserting the lines below, and saving your settings.

<pre>
{
  "translate_tabs_to_spaces": true,
  "tab_size": 2,
  "ensure_newline_at_eof_on_save": false,
  "default_encoding": "UTF-8",
  "default_line_ending": "lf",
  "trim_trailing_white_space_on_save": true
}
</pre>

### Sublime Packages

Sublime does not include every syntax highlight. To get certain highlights, you have to install them by hand. The instructions below delve into the install processes for __Jekyll__, __LESS__, and __Liquid__.

#### Package Control

Use [Package Control](http://sublime.wbond.net), Sublime's built-in tool, to install these syntaxes.

If you have Package Control, skip the rest of this and click any of the links below. If you don't, this [install guide](http://sublime.wbond.net/installation) will walk you through all the install options. Once that's done, click any of these links:

* [Jekyll](#jekyll)
* [LESS](#less)
* [Liquid](#liquid)

##### Jekyll

1. Open Preferences > Package Control.
2. Type `Install Package` and hit return.
3. Type `Jekyll` and hit return.

> The Jekyll package includes syntaxes for HTML, JSON, Markdown, and Textile.

##### LESS

1. Open Preferences > Package Control.
2. Type `Install Package` and hit return.
3. Type `LESS` and hit return.

##### Liquid

1. Open Preferences > Package Control.
2. Type `Install Package` and hit return.
3. Type `Siteleaf Liquid Syntax` and hit return.

> The Liquid package includes syntax for HTML.

---

## Running into Problems?

Below are a few issues and solutions that we came across during development.

#### Incompatible character encodings

* Problem: Getting **Liquid Exception: incompatible character encodings: UTF-8 and IBM437...** errors after running `grunt serve`.
* Cause: The CLI does not use UTF-8 by default (example: Git for Windows).
* Solution: Run these commands before running `grunt serve`.

```bash
$ cmd
$ chcp 65001
$ exit
```

> You only need to run these commands when you first open your CLI. The settings persist locally until you close it.

#### Conversion error

* Problem: Getting **Conversion error: There was an error converting *file_name.md*"** errors.
* Cause: A HTML tag is not closed.
* Solution: Close all HTML tags. Run `grunt test` to help find the open tag.

#### Liquid Exception: Cannot find /bin/sh

* Problem: Getting **Liquid Exception: Cannot find /bin/sh**.
* Cause: A buggy version of `pygments.rb`.
* Solution: Use `pygments.rb` version 0.5.0. This means you'll have to uninstall newer versions as well. Run the following commands.

        $ gem uninstall pygments.rb --version "=0.5.4"
        $ gem uninstall pygments.rb --version "=0.5.2"
        $ gem uninstall pygments.rb --version "=0.5.1"
        $ gem install pygments.rb --version "=0.5.0"
