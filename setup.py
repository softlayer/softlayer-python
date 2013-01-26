from setuptools import setup
import sys
import os

# Python 3 conversion
extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

requires = ['distribute']
if sys.version_info >= (2, 6):
    requires.append('requests')

description = "A library to contact SoftLayer's backend services"

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
    version='2.0.0',
    description=description,
    long_description=long_description,
    author='SoftLayer Technologies, Inc.',
    author_email='sldn@softlayer.com',
    packages=['SoftLayer', 'SoftLayer.tests', 'SoftLayer.transport'],
    license='The BSD License',
    zip_safe=False,
    url='http://github.com/softlayer/softlayer-api-python-client',
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
