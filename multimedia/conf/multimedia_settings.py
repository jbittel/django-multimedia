from django.conf import settings

MEDIA_SERVER_HOST = getattr(settings, "MEDIA_SERVER_HOST", "")
MEDIA_SERVER_USER = getattr(settings, "MEDIA_SERVER_USER", "")
MEDIA_SERVER_PASSWORD = getattr(settings, "MEDIA_SERVER_PASSWORD", "")
MEDIA_SERVER_PORT = getattr(settings, "MEDIA_SERVER_PORT", 22)
MEDIA_SERVER_AUDIO_PATH = getattr(settings, "MEDIA_SERVER_AUDIO_PATH", "")
MEDIA_SERVER_VIDEO_PATH = getattr(settings, "MEDIA_SERVER_VIDEO_PATH", "")

MULTIMEDIA_NOTIFICATION_EMAIL = getattr(settings, "MULTIMEDIA_NOTIFICATION_EMAIL", settings.DEFAULT_FROM_EMAIL)

DEFAULT_VIDEO_PROFILES = {
    'Flash Video': {
        'encode': 'ffmpeg -y -i "%(input)s" -f mp4 -acodec libfaac -ab 128k -vcodec libx264 -b:v 690k -ac 1 -s 620x350 -r 30 "%(output)s"',
        'container': 'f4v',
    },
}

DEFAULT_THUMBNAIL_CMD = 'ffmpeg -y -itsoffset -%(offset)d -i "%(input)s" -vcodec mjpeg -vframes 1 -an -f rawvideo -s 620x350 "%(output)s"'

MULTIMEDIA_VIDEO_PROFILES = getattr(settings, "MULTIMEDIA_VIDEO_PROFILES", DEFAULT_VIDEO_PROFILES)
MULTIMEDIA_THUMBNAIL_CMD = getattr(settings, 'MULTIMEDIA_THUMBNAIL_CMD', DEFAULT_THUMBNAIL_CMD)

DEFAULT_AUDIO_PROFILES = {
    'MP3 Audio': {
        'encode': 'ffmpeg -y -i "%(input)s" "%(output)s"',
        'container': 'mp3',
    },
}

MULTIMEDIA_AUDIO_PROFILES = getattr(settings, "MULTIMEDIA_AUDIO_PROFILES", DEFAULT_AUDIO_PROFILES)
