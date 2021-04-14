

# Versions

This project follows the Major.Minor.Revision versioning system. Fixes, and minor additions would increment Revision. Large changes and additions would increment Minor, and anything that would be a "Breaking" change, or redesign would be an increment of Major.

# Changelog

When doing a release, the Changelog format should be as follows:

```markdown

## [Version] - YYYY-MM-DD
https://github.com/softlayer/softlayer-python/compare/v5.9.0...v5.9.1 

#### New Command
- `slcli new command` #issueNumber

#### Improvements
- List out improvements #issueNumber
- Something else that changed #issueNumber

#### Deprecated
- List something that got removed #issueNumber

```

# Normal Release steps

A "release" of the softlayer-python project is the current state of the `master` branch. Any changes in the master branch should be considered releaseable.


1. Create the changelog entry, us this to update `CHANGELOG.md` and as the text for the release on github.
2. Update the version numbers in these files on the master branch.
    - `SoftLayer/consts.py`
    - `setup.py`
3. Make sure the tests for the build all pass
4. [Draft a new release](https://github.com/softlayer/softlayer-python/releases/new)
    - Version should start with `v` followed by Major.Minor.Revision: `vM.m.r`
    - Title should be `M.m.r`
    - Description should be the release notes  
    - Target should be the `master` branch
5. The github automation should take care of publishing the release to [PyPi](https://pypi.org/project/SoftLayer/). This may take a few minutes to update.

# Manual Release steps

1. Create the changelog entry, us this to update `CHANGELOG.md` and as the text for the release on github.
2. Update the version numbers in these files on the master branch.
    - `SoftLayer/consts.py`
    - `setup.py`
3. Commit your changes to `master`, and make sure `softlayer/softlayer-python` repo is updated to reflect that
4. Make sure your `upstream` repo is set

```
git remote -v
upstream  git@github.com:softlayer/softlayer-python.git (fetch)
upstream  git@github.com:softlayer/softlayer-python.git (push)
```

5. Create and publish the package
    - Make sure you have `twine` installed, this is what uploads the pacakge to PyPi.
    - Before you do this, make sure you have the organization repository set up as upstream remote, also make sure that you have pip set up with your PyPi user credentials. The easiest way to do that is to create a file at `~/.pypirc` with the following contents: 

 ```
[server-login]
username:YOUR_USERNAME
password:YOUR_PASSWORD
 ```

    - Run `python fabfile.py 5.7.2`. Where `5.7.2` is the `M.m.r` version number. Don't use the `v` here in the version number. 


*NOTE* PyPi doesn't let you reupload a version, if you upload a bad package for some reason, you have to create a new version.

