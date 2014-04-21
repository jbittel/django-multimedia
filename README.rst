django-multimedia
=================

Encode multimedia from the Django admin interface. Supports any encoding
profile you can write a command line statement to accomplish.

::

   Please note: this project is currently in a state of transition, and much
   of the documentation below is out-of-date. It will be updated in the near
   future to reflect the latest changes.

Getting Started
---------------

To get started simply install using ``pip``::

   $ pip install django-multimedia

Add ``multimedia`` to your installed apps and ``syncdb``. If you are using
``south`` you might want to ``syncdb --all`` and ``migrate --fake``

Your installed apps should look something like this::

   INSTALLED_APPS = (
       # ...existing apps...
       'multimedia',
   )

Next, you'll need to configure your settings. See **configuration** below.

Please refer to the documentation for each dependency on instructions on
how to install and configure them.

Configuration
-------------

Encoding profiles need to be set up for encoding media. These profiles are
created within the Django admin and require three things:

   #. ``Name``: a display name for the profile
   #. ``Container``: the filename extension for the output file
   #. ``Command``: the command line statement to accomplish the encoding

Each command needs to include both the ``%(input)s`` and ``%(output)s``
placeholders for the input and output filenames respectively. The commands
may call any available command line statement to encode the media.

A set of encoding profiles using ``ffmpeg`` is provided as a starting point.
They may be used as-is, or as an example of how to write your own. These
profiles may be loaded into the database with::

   $ manage.py loaddata encode-profiles

Note that this will remove any profiles that have already been created.

The following settings are used to upload the media after encoding::

   MEDIA_SERVER_HOST = "media.example.com"
   MEDIA_SERVER_USER = "username"
   MEDIA_SERVER_PASSWORD = "password"
   MEDIA_SERVER_PORT = 22
   MEDIA_SERVER_PATH = "upload/path/on/host"
