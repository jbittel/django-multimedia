import os
from shutil import rmtree

from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string

from celery.decorators import task
from celery.utils.log import get_task_logger

from conf import multimedia_settings

from .models import EncodeProfile
from .utils import upload_file


logger = get_task_logger(__name__)


@task(max_retries=3)
def encode_media(model, media_id, profile_id, tmpdir):
    media_type = ContentType.objects.get(app_label='multimedia', model=model)
    media = media_type.get_object_for_this_type(pk=media_id)
    profile = EncodeProfile.objects.get(pk=profile_id)
    logger.info("Encoding %s to %s" % (media, profile))
    try:
        encode_path = profile.encode(media, tmpdir)
    except Exception as exc:
        logger.info("Encoding failed for %s, retrying" % media)
        raise encode_media.retry(exc=exc, countdown=60)
    logger.info("Finished encoding %s to %s" % (media, profile))
    return encode_path


@task(max_retries=3)
def upload_media(encode_path, model, media_id):
    """
    Upload an encoded media file to the configured remote
    media server. The remote path is based off of the media
    server path setting and the encoded media filename.
    """
    filename = os.path.basename(encode_path)
    remote_path = os.path.join(multimedia_settings.MEDIA_SERVER_PATH,
                               model, str(media_id), filename)
    logger.info("Uploading %s to %s" % (filename, remote_path))
    try:
        upload_file(encode_path, remote_path)
    except Exception as exc:
        logger.info("Upload failed for %s, retrying" % filename)
        raise upload_media.retry(exc=exc, countdown=60)
    logger.info("Finished uploading %s to %s" % (filename, remote_path))


@task
def encode_media_complete(model, media_id, tmpdir):
    media_type = ContentType.objects.get(app_label='multimedia', model=model)
    media = media_type.get_object_for_this_type(pk=media_id)
    media.encoding = False
    media.encoded = True
    media.save()

    # Delete temporary encode directory
    rmtree(tmpdir)

    subject = "Multimedia Uploaded (%s)" % media.title
    message = render_to_string("multimedia/email_notification.txt", {"media": media})
    from_email = multimedia_settings.MULTIMEDIA_NOTIFICATION_EMAIL
    media.owner.email_user(subject, message, from_email=from_email)


@task(max_retries=3, ignore_result=True)
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
