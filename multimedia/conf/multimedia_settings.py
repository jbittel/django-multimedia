from django.conf import settings

MEDIA_SERVER_HOST = getattr(settings, "MEDIA_SERVER_HOST", "")
MEDIA_SERVER_USER = getattr(settings, "MEDIA_SERVER_USER", "")
MEDIA_SERVER_PASSWORD = getattr(settings, "MEDIA_SERVER_PASSWORD", "")
MEDIA_SERVER_PORT = getattr(settings, "MEDIA_SERVER_PORT", 22)
MEDIA_SERVER_VIDEO_BUCKET = getattr(settings, "MEDIA_SERVER_VIDEO_BUCKET", "")
MEDIA_SERVER_AUDIO_BUCKET = getattr(settings, "MEDIA_SERVER_AUDIO_BUCKET", "")
MEDIA_SERVER_AUDIO_PATH = getattr(settings, "MEDIA_SERVER_AUDIO_PATH", "")
MEDIA_SERVER_VIDEO_PATH = getattr(settings, "MEDIA_SERVER_VIDEO_PATH", "")

MULTIMEDIA_NOTIFICATION_EMAIL = getattr(settings, "MULTIMEDIA_NOTIFICATION_EMAIL", "")

DEFAULT_VIDEO_PROFILES = {
    'f4v': {
        'encode_cmd': 'ffmpeg -y -i "%(input)s" -f mp4 -acodec libfaac -ab 128k -vcodec libx264 -vpre slow -b 690k -ac 2 -crf 22 -s 620x350 -r 30 "%(output)s"',
        'encode':True,
        'name':'Flash Video',
        'container':'f4v',
        'thumbnail_cmd': 'ffmpeg -y -itsoffset -%(offset)s -i "%(input)s" -vcodec mjpeg -vframes 1 -an -f rawvideo -s 620x350 "%(output)s"'
    },
}

MULTIMEDIA_VIDEO_PROFILES = getattr(settings, "MULTIMEDIA_VIDEO_PROFILES", DEFAULT_VIDEO_PROFILES)

DEFAULT_AUDIO_PROFILES = {
    'audio': {
        'encode_cmd': 'ffmpeg -y -i "%(input)s" "%(output)s"',
        'encode':True,
        'name':'MP3 Audio',
        'container':'mp3',
    },
}

MULTIMEDIA_AUDIO_PROFILES = getattr(settings, "MULTIMEDIA_AUDIO_PROFILES", DEFAULT_AUDIO_PROFILES)

MULTIMEDIA_APP_LABLEL = getattr(settings, "MULTIMEDIA_APP_LABEL", "Multimedia")