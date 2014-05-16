.. _installation:

Installation
============

Installing
----------

Installing the latest release is easiest with ``pip``::

   $ pip install django-multimedia

This will also install all appropriate dependencies.

Configuring
-----------

The first step is to add both ``django-storages`` and ``django-multimedia``
to your project's ``INSTALLED_APPS``::

   INSTALLED_APPS = (
       # ...existing apps...
       'storage',
       'multimedia',
   )

Once these apps are added, update your database::

   $ ./manage.py syncdb
   $ ./manage.py migrate multimedia

You also need to configure an appropriate storage backend for uploading
encoded media. The setting ``MULTIMEDIA_FILE_STORAGE`` should be set to
a dotted path specifying the selected backend. For example, for uploading
encoded media using SFTP::

   MULTIMEDIA_FILE_STORAGE = 'storages.backends.sftpstorage.SFTPStorage'

Additionally, you will need to configure the selected backend. For more
information, see the `django-storages documentation`_.

Encoding Profiles
-----------------

Encoding profiles need to be set up for encoding media. These profiles are
created within the Django admin and require three things:

   #. ``Name``: a display name for the profile
   #. ``Container``: the filename extension for the output file
   #. ``Command``: the command line statement to accomplish the encoding

Each command needs to include both ``%(input)s`` and ``%(output)s``
placeholders for the input and output filenames, respectively. The commands
may call any available command line statement to encode the media.

A set of encoding profiles using ``ffmpeg`` is provided as a starting point.
They may be used as-is, or as an example of how to write your own. These
profiles may be loaded into the database with::

   $ manage.py loaddata encode-profiles

Note that this command will remove any previously created profiles.

.. _django-storages documentation: http://django-storages.readthedocs.org/
