# Code Organization

Below is the basic spread for our source.

<output>
├─<i class="fa fa-folder-open-o fa-fw"></i> SoftLayer
│  ├─<i class="fa fa-folder-open-o fa-fw"></i> CLI
│     └─<i class="fa fa-folder-o fa-fw"></i> modules
│  ├─<i class="fa fa-folder-o fa-fw"></i> managers
│  └─<i class="fa fa-folder-o fa-fw"></i> tests
├─<i class="fa fa-folder-o fa-fw"></i> docs
└─<i class="fa fa-folder-o fa-fw"></i> tools
</output>

This table is an overview of each directory.

| Directory              | Subdirectory             | Contents            |
| ---------------------- | ------------------------ | ------------------- |
| <samp>SoftLayer</samp> | <samp>-</samp>           | Python bindings for the API |
| <samp>SoftLayer</samp> | <samp>CLI</samp>         | Source code for CLI |
| <samp>SoftLayer</samp> | <samp>CLI/modules</samp> | Pluggable modules for CLI |
| <samp>SoftLayer</samp> | <samp>managers</samp>    | Helpers for making API calls |
| <samp>SoftLayer</samp> | <samp>tests</samp>       | Unit tests for API, CLI, and Managers |
| <samp>docs</samp>      | <samp>-</samp>           | Raw content for <a href="http://softlayer-python.readthedocs.org/en/latest" target="_blank">Python Client</a> |
| <samp>tools</samp>     | <samp>-</samp>           | Production and testing dependencies |

> Several subdirectories were not mentioned deliberately since they're reserved for our doc content.
