# Source Control

In order to maintain dependencies, backward compatibility, and merges from pull requests, we follow the <a href="http://semver.org" target="_blank">Semantic Versioning</a> guidelines. This means each release is pegged with the `<major>.<minor>.<patch>` scheme. It also means each release adheres strictly to the following guidelines:

* Breaking backward compatibility bumps up the major and resets the minor and patch
* Adding new features or enhancements without breaking backward compatibility bumps up the minor and resets the patch
* Bug fixes and miscellaneous changes bumps up the patch
