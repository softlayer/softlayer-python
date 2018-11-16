from __future__ import print_function
import codecs
import os

from setuptools import setup, find_packages

DESCRIPTION = "A library for SoftLayer's API"

if os.path.exists('README.rst'):
    with codecs.open('README.rst', 'r', 'utf-8') as readme_file:
        LONG_DESCRIPTION = readme_file.read()
else:
    LONG_DESCRIPTION = DESCRIPTION

setup(
    name='SoftLayer',
    version='5.6.4',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author='SoftLayer Technologies, Inc.',
    author_email='sldn@softlayer.com',
    packages=find_packages(exclude=['tests']),
    license='MIT',
    zip_safe=False,
    url='http://github.com/softlayer/softlayer-python',
    entry_points={
        'console_scripts': [
            'slcli = SoftLayer.CLI.core:main',
            'sl = SoftLayer.CLI.deprecated:main',
        ],
    },
    install_requires=[
        'six >= 1.7.0',
        'ptable >= 0.9.2',
        'click >= 7',
        'requests >= 2.20.0',
        'prompt_toolkit >= 0.53',
        'pygments >= 2.0.0',
        'urllib3 >= 1.24'
    ],
    keywords=['softlayer', 'cloud', 'slcli'],
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
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
