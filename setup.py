import sys
import os

try:
    from setuptools import setup
except ImportError:
    print("Distribute is required for install:")
    print("    http://python-distribute.org/distribute_setup.py")
    sys.exit(1)

# Not supported for Python versions < 2.6
if sys.version_info <= (2, 6):
    print("Python 2.6 or greater is required.")
    sys.exit(1)

extra = {}

requires = [
    'six >= 1.1.0',
    'prettytable >= 0.7.0',
    'docopt == 0.6.1',
    'requests',
]

if sys.version_info < (2, 7):
    requires.append('importlib')

description = "A library for SoftLayer's API"

if os.path.exists('README.rst'):
    f = open('README.rst')
    try:
        long_description = f.read()
    finally:
        f.close()
else:
    long_description = description

setup(
    name='SoftLayer',
    version='3.1.0',
    description=description,
    long_description=long_description,
    author='SoftLayer Technologies, Inc.',
    author_email='sldn@softlayer.com',
    packages=[
        'SoftLayer',
        'SoftLayer.CLI',
        'SoftLayer.CLI.modules',
        'SoftLayer.managers',
    ],
    license='MIT',
    zip_safe=False,
    url='http://github.com/softlayer/softlayer-api-python-client',
    entry_points={
        'console_scripts': [
            'sl = SoftLayer.CLI.core:main',
        ],
    },
    package_data={
        'SoftLayer': ['tests/fixtures/*.conf'],
    },
    test_suite='nose.collector',
    install_requires=requires,
    classifiers=[
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
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
