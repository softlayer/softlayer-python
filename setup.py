from __future__ import print_function
import sys
import os

from codecs import open

try:
    from setuptools import setup, find_packages
except ImportError:
    print("Distribute is required for install:")
    print("    http://python-distribute.org/distribute_setup.py")
    sys.exit(1)

# Not supported for Python versions < 2.6
if sys.version_info <= (2, 6):
    print("Python 2.6 or greater is required.")
    sys.exit(1)

REQUIRES = [
    'six >= 1.7.0',
    'prettytable >= 0.7.0',
    'click',
    'requests >= 2.7.0',
]

if sys.version_info < (2, 7):
    REQUIRES.append('importlib')

DESCRIPTION = "A library for SoftLayer's API"

if os.path.exists('README.rst'):
    with open('README.rst', 'r', 'utf-8') as readme_file:
        LONG_DESCRIPTION = readme_file.read()
else:
    LONG_DESCRIPTION = DESCRIPTION

setup(
    name='SoftLayer',
    version='4.0.3',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author='SoftLayer Technologies, Inc.',
    author_email='sldn@softlayer.com',
    packages=find_packages(exclude=["SoftLayer.tests"]),
    license='MIT',
    zip_safe=False,
    url='http://github.com/softlayer/softlayer-python',
    entry_points={
        'console_scripts': [
            'slcli = SoftLayer.CLI.core:main',
            'sl = SoftLayer.CLI.deprecated:main',
        ],
    },
    test_suite='nose.collector',
    install_requires=REQUIRES,
    keywords=['softlayer', 'cloud'],
    classifiers=[
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
