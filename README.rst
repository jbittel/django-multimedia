django-multimedia
=================

A Django app used to encode video from the Django admin. Supports any video
profile you can write a command line statement to accomplish.
::
   Please note: this project is currently in a state of transition, and much
   of the documentation below is out-of-date. It will be updated in the near
   future to reflect the latest changes.

Dependencies
------------

- django-celery
- django-filer
- paramiko
- pycrpto
- ffmpeg

Getting Started
---------------

To get started simply install using ``pip``:
::
    pip install django-multimedia

Add ``multimedia`` to your installed apps and ``syncdb``.  If you are using ``south`` you might want to ``syncdb --all`` and ``migrate --fake``

Your installed apps should look something like this:
::
	INSTALLED_APPS = (
	    'django.contrib.auth',
	    'django.contrib.contenttypes',
	    'django.contrib.sessions',
	    'django.contrib.sites',
	    'django.contrib.messages',
	    'django.contrib.admin',
	    'djcelery',
	    'filer',
	    'multimedia',
	    'appmedia',
	    'easy_thumbnails',
	)

Next, you'll need to configure your settings. See **configuration** below.

Please refer to the documentation for each dependency on instructions on how to install them.

Configuration
-------------

You'll need to configure your media profiles and tell the app where to upload the encoded file to after completion.  You can use any ``ffmpeg`` command as long as you have the codecs needed installed.  Use the settings ''MULTIMEDIA_VIDEO_PROFILES'' and ''MULTIMEDIA_AUDIO_PROFILES''  to accomplish this.  

The following is the default profile for Video.
::
    MULTIMEDIA_VIDEO_PROFILES = {
        'f4v': {
            'encode_cmd': 'ffmpeg -y -i "%(input)s" -f mp4 -acodec libfaac -ab 128k -vcodec libx264 -vpre slow -b 690k -ac 1 -s 620x350 -r 30 "%(output)s"',
            'encode':True,
            'name':'Flash Video',
            'container':'f4v',
            'thumbnail_cmd': 'ffmpeg -y -itsoffset -%(offset)s -i "%(input)s" -vcodec mjpeg -vframes 1 -an -f rawvideo -s 620x350 "%(output)s"'
        },
    }

Here is a breakdown of the ``ffmpeg`` arguments being used in these examples.
::
    Video: 
    ffmpeg 
    -y // Answer YES to all prompts
    -i "%(input)s" // Input file path put in automatically by the system, leave this alone
    -f mp4 // Video container
    -acodec libfaac // Audio codec
    -ac 1 // Audio channels 
    -ab 128k // Audio bitrate
    -vcodec libx264 // Video codec
    -vpre slow // Preset for video encoding quality (slow, fast, medium, etc)
    -b 690k // Video bitrate
    -s 620x350 // File dimensions
    -r 30 // Framerate
    "%(output)s" // Output file path put in automatically by the system, leave this alone

    Screenshot: 
    ffmpeg 
    -y // Answer YES to all prompts
    -itsoffset -%(offset)s // Frame offset, how far into the video to grab a screenshot, leave this alone
    -i "%(input)s" // Input file path put in automatically by the system, leave this alone
    -vcodec mjpeg // Video (image) codec
    -vframes 1 // We only want a single frame
    -an // No clue what this does
    -f rawvideo // Output image format
    -s 620x350 // File dimensions
    "%(output)s" // Output file path put in automatically by the system, leave this alone

And here is the default profile for Audio:
::
    MULTIMEDIA_AUDIO_PROFILES = {
        'audio': {
            'encode_cmd': 'ffmpeg -y -i "%(input)s" "%(output)s"',
            'encode':True,
            'name':'MP3 Audio',
            'container':'mp3',
        },
    }

The following settings are used to upload the media after encoding:
::
    MEDIA_SERVER_HOST = "some.host.here"
    MEDIA_SERVER_USER = "host_user"
    MEDIA_SERVER_PASSWORD = "user_pwd"
    MEDIA_SERVER_PORT = 22
    MEDIA_SERVER_VIDEO_BUCKET = "videobucket"
    MEDIA_SERVER_AUDIO_BUCKET = "audiobucket"
    MEDIA_SERVER_AUDIO_PATH = "path/on/some/server" % (MEDIA_SERVER_AUDIO_BUCKET,)
    MEDIA_SERVER_VIDEO_PATH = "path/on/some/server" % (MEDIA_SERVER_VIDEO_BUCKET,)
   
Installing FFMPEG
-----------------

On Mac OS X you should be able to install ``ffmpeg`` using ``homebrew``:
::
    brew install ffmpeg

You might need to ``brew`` install other codecs you want to use as well.

On Ubuntu, here is a link to a helpful guide with instructions on how to install on different Ubuntu versions: http://ubuntuforums.org/showthread.php?t=786095
