#!/usr/bin/env python

from setuptools import setup, find_packages
import os

from multimedia import __version__ as version


install_requires = [
    'setuptools',
    'django-celery',
    'django-filer',
    'paramiko',
    'pycrypto==2.0.1',
]


setup(
    name='django-multimedia',
    version=version,
    url='http://github.com/jbittel/django-multimedia',
    license='BSD',
    description='',
    author='Jason Bittel',
    author_email='jason.bittel@gmail.com',
    package_dir={'multimedia': 'multimedia'},
    packages=find_packages(),
    install_requires=install_requires,
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Multimedia :: Video',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia :: Video :: Conversion',
    ],
)
