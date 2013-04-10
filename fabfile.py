from fabric.api import local, lcd, settings


def publish_docs():
    " Publishes docs to github via github pages. "
    with lcd('docs'):
        with settings(warn_only=True):
            local('rm -rf _build/html')
            local('mkdir -p _build/html')
        local('git clone -b gh-pages '
              'git@github.com:softlayer/softlayer-api-python-client.git '
              '_build/html')
        local('make html')
        with lcd('_build/html'):
            local('touch .nojekyll')
            local('git add .nojekyll')
            local('git add -A')
            local('git commit -m "Documentation Build"')
            local('git push origin gh-pages')


def make_html():
    "Build HTML docs"
    with lcd('docs'):
        local('make html')
