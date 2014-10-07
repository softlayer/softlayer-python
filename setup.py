import sys
import os

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

extra = {}

requires = [
    'six >= 1.7.0',
    'prettytable >= 0.7.0',
    'click',
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
    version='3.2.0',
    description=description,
    long_description=long_description,
    author='SoftLayer Technologies, Inc.',
    author_email='sldn@softlayer.com',
    packages=find_packages(exclude=["SoftLayer.tests"]),
    license='MIT',
    zip_safe=False,
    url='http://github.com/softlayer/softlayer-python',
    entry_points={
        'console_scripts': [
            'sl = SoftLayer.CLI.core:main',
        ],
        'softlayer.cli': [
            'vs = SoftLayer.CLI.virt',
            'vs:cancel = SoftLayer.CLI.virt.cancel:cli',
            'vs:capture = SoftLayer.CLI.virt.capture:cli',
            'vs:create = SoftLayer.CLI.virt.create:cli',
            'vs:create-options = SoftLayer.CLI.virt.create_options:cli',
            'vs:detail = SoftLayer.CLI.virt.detail:cli',
            'vs:dns-sync = SoftLayer.CLI.virt.dns:cli',
            'vs:edit = SoftLayer.CLI.virt.edit:cli',
            'vs:list = SoftLayer.CLI.virt.list:cli',
            'vs:network = SoftLayer.CLI.virt.network:cli',
            'vs:rescue = SoftLayer.CLI.virt.power:rescue',
            'vs:power_off = SoftLayer.CLI.virt.power:power_off',
            'vs:power_on = SoftLayer.CLI.virt.power:power_on',
            'vs:pause = SoftLayer.CLI.virt.power:pause',
            'vs:resume = SoftLayer.CLI.virt.power:resume',
            'vs:ready = SoftLayer.CLI.virt.ready:cli',
            'vs:reload = SoftLayer.CLI.virt.reload:cli',
            'vs:upgrade = SoftLayer.CLI.virt.upgrade:cli',

            'cdn = SoftLayer.CLI.cdn',
            'cdn:detail = SoftLayer.CLI.cdn.detail:cli',
            'cdn:list = SoftLayer.CLI.cdn.list:cli',
            'cdn:load = SoftLayer.CLI.cdn.load:cli',
            'cdn:origin-add = SoftLayer.CLI.cdn.origin_add:cli',
            'cdn:origin-list = SoftLayer.CLI.cdn.origin_list:cli',
            'cdn:origin-remove = SoftLayer.CLI.cdn.origin_remove:cli',
            'cdn:purge = SoftLayer.CLI.cdn.purge:cli',

            'config = SoftLayer.CLI.config',
            'config:setup = SoftLayer.CLI.config.setup:cli',
            'config:show = SoftLayer.CLI.config.show:cli',

            'dns = SoftLayer.CLI.dns',
            'dns:record-add = SoftLayer.CLI.dns.record_add:cli',
            'dns:record-list = SoftLayer.CLI.dns.record_list:cli',
            'dns:record-remove = SoftLayer.CLI.dns.record_remove:cli',
            'dns:zone-create = SoftLayer.CLI.dns.zone_create:cli',
            'dns:zone-delete = SoftLayer.CLI.dns.zone_delete:cli',
            'dns:zone-list = SoftLayer.CLI.dns.zone_list:cli',
            'dns:zone-print = SoftLayer.CLI.dns.zone_print:cli',

            'firewall = SoftLayer.CLI.firewall',
            'firewall:add = SoftLayer.CLI.firewall.add:cli',
            'firewall:cancel = SoftLayer.CLI.firewall.cancel:cli',
            'firewall:detail = SoftLayer.CLI.firewall.detail:cli',
            'firewall:edit = SoftLayer.CLI.firewall.edit:cli',
            'firewall:list = SoftLayer.CLI.firewall.list:cli',

            'globalip = SoftLayer.CLI.globalip',
            'globalip:assign = SoftLayer.CLI.globalip.assign:cli',
            'globalip:cancel = SoftLayer.CLI.globalip.cancel:cli',
            'globalip:detail = SoftLayer.CLI.globalip.create:cli',
            'globalip:list = SoftLayer.CLI.globalip.list:cli',
            'globalip:unassign = SoftLayer.CLI.globalip.unassign:cli',

            'summary = SoftLayer.CLI.summary:cli',
        ]
    },
    package_data={'SoftLayer': ['tests/fixtures/*.conf']},
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
