from fabric.api import local, lcd


def make_html():
    "Build HTML docs"
    with lcd('docs'):
        local('make html')
