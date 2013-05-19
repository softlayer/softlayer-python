try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup  # NOQA
import sys
import os

# Not supported for Python versions < 2.6
if sys.version_info <= (2, 6):
    print("Python 2.6 or greater is required.")
    sys.exit(1)

# Python 3 conversion
extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

requires = [
    'distribute',
    'prettytable',
    'docopt==0.6.1',
    'requests'
]

if sys.version_info < (2, 7):
    requires.append('importlib')

description = "A library to use SoftLayer's API"

if os.path.exists('README.md'):
    f = open('README.md')
    try:
        long_description = f.read()
    finally:
        f.close()
else:
    long_description = description

setup(
    name='SoftLayer',
    version='2.2.0',
    description=description,
    long_description=long_description,
    author='SoftLayer Technologies, Inc.',
    author_email='sldn@softlayer.com',
    packages=[
        'SoftLayer',
        'SoftLayer.CLI',
        'SoftLayer.CLI.modules',
        'SoftLayer.tests',
        'SoftLayer.tests.API',
        'SoftLayer.tests.CLI'
    ],
    license='The BSD License',
    zip_safe=False,
    url='http://github.com/softlayer/softlayer-api-python-client',
    entry_points={
        'console_scripts': [
            'sl = SoftLayer.CLI.core:main',
        ],
    },
    package_data={
        'SoftLayer': ['tests/fixtures/*'],
    },
    install_requires=requires,
    classifiers=[
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    **extra
)
