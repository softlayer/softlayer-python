import os.path
import shutil

from fabric.api import local, lcd, puts, abort


def make_html():
    "Build HTML docs"
    with lcd('docs'):
        local('make html')


def upload():
    "Upload distribution to PyPi"
    local('python setup.py sdist upload')
    local('python setup.py bdist_wheel upload')


def clean():
    puts("* Cleaning Repo")
    directories = ['.tox', 'SoftLayer.egg-info', 'build', 'dist']
    for directory in directories:
        if os.path.exists(directory) and os.path.isdir(directory):
            shutil.rmtree(directory)


def release(version, force=False):
    """Perform a release. Example:

    $ fab release:3.0.0

    """
    if version.startswith("v"):
        abort("Version should not start with 'v'")
    version_str = "v%s" % version

    clean()

    local("pip install wheel")

    puts(" * Uploading to PyPI")
    upload()

    puts(" * Tagging Version %s" % version_str)
    force_option = 'f' if force else ''
    local("git tag -%sam \"%s\" %s" % (force_option, version_str, version_str))

    puts(" * Pushing Tag to upstream")
    local("git push upstream %s" % version_str)
