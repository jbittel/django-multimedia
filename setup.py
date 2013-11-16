#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from multimedia import __version__ as version


packages = [
    'multimedia',
    'multimedia.conf',
    'multimedia.migrations',
]

package_data = {
    '': ['AUTHORS', 'LICENSE', 'README.rst'],
    'multimedia': ['fixtures/*.json',
                   'templates/multimedia/*.html', 'templates/multimedia/*.txt'],
}

install_requires = [
    'django-celery',
    'django-filer',
    'paramiko',
]

with open('README.rst') as f:
    readme = f.read()

setup(
    name='django-multimedia',
    version=version,
    url='http://github.com/jbittel/django-multimedia',
    license='BSD',
    description='A Django app for encoding and uploading video within the '
                'Django admin. Supports any video profile you can write a '
                'command line statement to accomplish.',
    long_description=readme,
    author='Jason Bittel',
    author_email='jason.bittel@gmail.com',
    package_dir={'multimedia': 'multimedia'},
    packages=packages,
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
