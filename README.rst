django-multimedia
=================

Encode and upload multimedia from the Django admin interface. Supports any
encoding profile you can write a command line statement to accomplish.

Quick start
-----------

Install with `pip`_::

   $ pip install django-multimedia

Add to ``INSTALLED_APPS``::

   INSTALLED_APPS += (
       'storage',
       'multimedia',
   )

Update your database::

   $ ./manage.py syncdb
   $ ./manage.py migrate multimedia

Configure your selected `storage backend`_::

   MULTIMEDIA_FILE_STORAGE = 'path.to.backend'

.. _pip: http://www.pip-installer.org/
.. _storage backend: http://django-storages.readthedocs.org/
