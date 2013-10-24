from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string

from celery.decorators import task
from celery.utils.log import get_task_logger

from conf import multimedia_settings

from .models import EncodeProfile


logger = get_task_logger(__name__)


@task(max_retries=3)
def encode_media(model, media_id, profile_id):
    media_type = ContentType.objects.get(app_label='multimedia', model=model)
    media = media_type.get_object_for_this_type(pk=media_id)
    profile = EncodeProfile.objects.get(pk=profile_id)
    logger.info("Encoding %s to %s" % (media, profile))
    try:
        media.encode_to_container(profile)
        media.upload_to_server(profile)
    except Exception as exc:
        logger.info("Encoding failed for %s, retrying" % media)
        raise encode_media.retry(exc=exc, countdown=60)
    logger.info("Finished encoding %s to %s" % (media, profile))


@task
def encode_media_complete(model, media_id):
    media_type = ContentType.objects.get(app_label='multimedia', model=model)
    media = media_type.get_object_for_this_type(pk=media_id)
    media.encoding = False
    media.encoded = True
    media.uploaded = True
    media.save()

    subject = "Multimedia Uploaded (%s)" % media.title
    message = render_to_string("multimedia/email_notification.txt", {"media": media})
    from_email = multimedia_settings.MULTIMEDIA_NOTIFICATION_EMAIL
    media.owner.email_user(subject, message, from_email=from_email)


@task(max_retries=3)
def generate_thumbnail(model, media_id):
    media_type = ContentType.objects.get(app_label='multimedia', model=model)
    media = media_type.get_object_for_this_type(pk=media_id)
    logger.info("Generating thumbnail for %s" % media)
    try:
        media.generate_thumbnail()
    except Exception as exc:
        logger.info("Thumbnail generation failed for %s, retrying" % media)
        raise generate_thumbnail.retry(exc=exc, countdown=60)
    logger.info("Done generating thumbnail for %s" % media)
