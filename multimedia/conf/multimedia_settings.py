from django.conf import settings

MEDIA_SERVER_HOST = getattr(settings, "MEDIA_SERVER_HOST", "")
MEDIA_SERVER_USER = getattr(settings, "MEDIA_SERVER_USER", "")
MEDIA_SERVER_PASSWORD = getattr(settings, "MEDIA_SERVER_PASSWORD", "")
MEDIA_SERVER_PORT = getattr(settings, "MEDIA_SERVER_PORT", 22)
MEDIA_SERVER_PATH = getattr(settings, "MEDIA_SERVER_PATH", "")
