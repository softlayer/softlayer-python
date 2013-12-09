import os.path
import shutil

from fabric.api import local, lcd, puts, abort


def make_html():
    "Build HTML docs"
    with lcd('docs'):
        local('make html')


def upload():
    "Upload distribution to PyPi"
    local('python setup.py sdist register upload')


def clean():
    puts("* Cleaning Repo")
    dirs = ['.tox', 'SoftLayer.egg-info', 'build', 'dist']
    for d in dirs:
        if os.path.exists(d) and os.path.isdir(d):
            shutil.rmtree(d)


def release(version, force=False):
    """Perform a release. Example:

    $ fab release:3.0.0

    """
    if version.startswith("v"):
        abort("Version should not start with 'v'")
    version_str = "v%s" % version

    clean()

    puts(" * Tagging Version %s" % version_str)
    f = 'f' if force else ''
    local("git tag -%sam \"%s\" %s" % (f, version_str, version_str))

    puts(" * Uploading to PyPI")
    upload()

    puts(" * Pushing Tag to upstream")
    local("git push upstream %s" % version_str)
