# Release steps

* Update version constants (find them by running `git grep [VERSION_NUMBER]`)
* Create changelog entry (edit CHANGELOG.md with a one-liner for each closed issue going in the release)
* Commit and push changes to master with the message: "Version Bump to v[VERSION_NUMBER]"
* Push tag and PyPi `fab release:[VERSION_NUMBER]`. Before you do this, make sure you have fabric installed (`pip install fabric`) and also make sure that you have pip set up with your PyPi user credentials. The easiest way to do that is to create a file at `~/.pypirc` with the following contents:

 ```
[server-login]
username:YOUR_USERNAME
password:YOUR_PASSWORD
 ```
