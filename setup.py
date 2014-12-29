#!/usr/bin/env python

from setuptools import find_packages
from setuptools import setup

from multimedia import __version__ as version


with open('README.rst') as f:
    readme = f.read()

setup(
    name='django-multimedia',
    version=version,
    description='Encode and upload multimedia from the Django admin interface',
    long_description=readme,
    license='BSD',
    author='Jason Bittel',
    author_email='jason.bittel@gmail.com',
    url='https://github.com/jbittel/django-multimedia',
    packages=find_packages(),
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
        'Topic :: Multimedia :: Video',
        'Topic :: Multimedia :: Video :: Conversion',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia :: Sound/Audio :: Conversion',
    ],
    keywords=['multimedia', 'media', 'audio', 'video', 'encoding', 'conversion'],
    install_requires=[
        'celery>=3.1',
        'django-storages',
    ],
)
