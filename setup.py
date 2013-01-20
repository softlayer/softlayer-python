from setuptools import setup
import sys

# Python 3 conversion
extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

description = "A library to contact SoftLayer's backend services"

try:
    long_description = read('README.md')
except:
    long_description = description

setup(
    name='SoftLayer',
    version='2.0.0',
    description=description,
    long_description=long_description,
    author='SoftLayer Technologies, Inc.',
    author_email='sldn@softlayer.com',
    packages=['SoftLayer', 'SoftLayer.tests'],
    license='The BSD License',
    zip_safe=False,
    url='http://github.com/softlayer/softlayer-api-python-client',
    install_requires=['distribute'],
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
