try:
    import distribute_setup
    distribute_setup.use_setuptools()
except ImportError:
    pass

from setuptools import setup
import sys

# Python 3 conversion
extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(
    name='SoftLayer',
    version='1.1',
    description="A library to contact SoftLayer's backend services",
    author='SoftLayer Technologies, Inc.',
    author_email='sldn@softlayer.com',
    packages=[
        'SoftLayer', 'tests'
    ],
    license='The BSD License',
    url='http://github.com/softlayer/softlayer-api-python-client',
    classifiers=[
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    **extra
)
