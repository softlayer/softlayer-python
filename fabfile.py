import click
import os.path
import shutil
import subprocess
import sys
from pprint import pprint as pp 

def make_html():
    """Build HTML docs"""
    click.secho("Building HTML")
    subprocess.run('make html', cwd='docs', shell=True)

def upload():
    """Upload distribution to PyPi"""
    cmd_setup = 'python setup.py sdist bdist_wheel'
    click.secho("\tRunning %s" % cmd_setup, fg='yellow')
    subprocess.run(cmd_setup, shell=True)
    cmd_twine = 'twine upload dist/*'
    click.secho("\tRunning %s" % cmd_twine, fg='yellow')
    subprocess.run(cmd_twine, shell=True)


def clean():
    click.secho("* Cleaning Repo")
    directories = ['.tox', 'SoftLayer.egg-info', 'build', 'dist']
    for directory in directories:
        if os.path.exists(directory) and os.path.isdir(directory):
            shutil.rmtree(directory)


@click.command()
@click.argument('version')
@click.option('--force',  default=False, is_flag=True, help="Force upload")
def release(version, force):
    """Perform a release. Example:

    $ python fabfile.py 1.2.3

    """
    if version.startswith("v"):
        exit("Version should not start with 'v'")
    version_str = "v%s" % version

    clean()

    subprocess.run("pip install wheel", shell=True)

    print(" * Uploading to PyPI")
    upload()
    make_html()

    force_option = 'f' if force else ''
    cmd_tag = "git tag -%sam \"%s\" %s" % (force_option, version_str, version_str)

    click.secho(" * Tagging Version %s" % version_str)
    click.secho("\tRunning %s" % cmd_tag, fg='yellow')
    subprocess.run(cmd_tag, shell=True)


    cmd_push = "git push upstream %s" % version_str
    click.secho(" * Pushing Tag to upstream")
    click.secho("\tRunning %s" % cmd_push, fg='yellow')
    subprocess.run(cmd_push, shell=True)


if __name__ == '__main__':
    release()