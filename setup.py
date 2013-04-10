from setuptools import setup, find_packages
import sys
import os

# Python 3 conversion
extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

requires = ['distribute', 'prettytable', 'docopt==0.6.1']

if sys.version_info < (2, 7):
    requires.append('importlib')
elif sys.version_info >= (2, 6):
    requires.append('requests')
if sys.version_info <= (2, 6):
    requires.append('simplejson')

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
    packages=find_packages(),
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
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    **extra
)
