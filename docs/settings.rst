.. _settings:

Settings
========

.. currentmodule:: django.conf.settings

.. attribute:: MULTIMEDIA_FILE_STORAGE

   Defines the `django-storages`_ backend that is used to upload encoded
   media. This is specified as a dotted path to the desired backend module.
   For example::

      MULTIMEDIA_FILE_STORAGE = 'storages.backends.sftpstorage.SFTPStorage'

   You will need to configure the selected backend according to its
   `respective documentation`_.

.. _django-storages: https://bitbucket.org/david/django-storages
.. _respective documentation: http://django-storages.readthedocs.org/
