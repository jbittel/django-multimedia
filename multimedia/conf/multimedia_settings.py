from django.conf import settings

MEDIA_SERVER_HOST = getattr(settings, "MEDIA_SERVER_HOST", "")
MEDIA_SERVER_USER = getattr(settings, "MEDIA_SERVER_USER", "")
MEDIA_SERVER_PASSWORD = getattr(settings, "MEDIA_SERVER_PASSWORD", "")
MEDIA_SERVER_PORT = getattr(settings, "MEDIA_SERVER_PORT", 22)
MEDIA_SERVER_PATH = getattr(settings, "MEDIA_SERVER_PATH", "")

DEFAULT_THUMBNAIL_CMD = 'ffmpeg -y -itsoffset -%(offset)d -i "%(input)s" -vcodec mjpeg -vframes 1 -an -f rawvideo -s 620x350 "%(output)s"'
MULTIMEDIA_THUMBNAIL_CMD = getattr(settings, 'MULTIMEDIA_THUMBNAIL_CMD', DEFAULT_THUMBNAIL_CMD)
