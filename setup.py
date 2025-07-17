from __future__ import print_function
import codecs
import os

from setuptools import setup, find_packages
# pylint: disable=inconsistent-return-statements

DESCRIPTION = "A library for SoftLayer's API"

if os.path.exists('README.rst'):
    with codecs.open('README.rst', 'r', 'utf-8') as readme_file:
        LONG_DESCRIPTION = readme_file.read()
else:
    LONG_DESCRIPTION = DESCRIPTION

setup(
    name='SoftLayer',
    version='v6.2.7',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/x-rst',
    author='SoftLayer, Inc., an IBM Company',
    author_email='SLDNDeveloperRelations@wwpdl.vnet.ibm.com',
    packages=find_packages(exclude=['tests']),
    license='MIT',
    zip_safe=False,
    url='https://github.com/SoftLayer/softlayer-python',
    entry_points={
        'console_scripts': [
            'slcli = SoftLayer.CLI.core:main',
        ],
    },
    python_requires='>=3.7',
    install_requires=[
        'click >= 8.0.4',
        'requests >= 2.32.2',
        'prompt_toolkit >= 2',
        'pygments >= 2.0.0',
        'urllib3 >= 1.24',
        'rich == 14.0.0'
    ],
    keywords=['softlayer', 'cloud', 'slcli', 'ibmcloud'],
    classifiers=[
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
