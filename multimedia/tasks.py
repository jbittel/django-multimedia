from __future__ import absolute_import

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

from celery import shared_task
from celery.utils.log import get_task_logger

from .models import EncodeProfile
from .models import RemoteStorage


logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=5)
def encode_media(self, model, media_id, profile_id):
    try:
        media_type = ContentType.objects.get(app_label='multimedia', model=model)
        media = media_type.get_object_for_this_type(pk=media_id)
        profile = EncodeProfile.objects.get(pk=profile_id)
        logger.info("Encoding %s to %s" % (media, profile))
        encode_path = profile.encode(media)
    except ObjectDoesNotExist as exc:
        raise self.retry(exc=exc, countdown=5)
    except Exception as exc:
        logger.info("Encoding failed for %s, retrying" % media)
        raise self.retry(exc=exc, countdown=60)
    logger.info("Finished encoding %s to %s" % (media, profile))
    return encode_path


@shared_task(bind=True, max_retries=3)
def upload_media(self, encode_path, model, media_id, profile_id):
    """
    Upload an encoded media file to the configured remote storage.
    """
    try:
        media_type = ContentType.objects.get(app_label='multimedia', model=model)
        media = media_type.get_object_for_this_type(pk=media_id)
        profile = EncodeProfile.objects.get(pk=profile_id)
    except ObjectDoesNotExist as exc:
        raise self.retry(exc=exc, countdown=5)

    try:
        storage = RemoteStorage.objects.get(content_type__pk=media_type.id,
                                            media_id=media.id, profile=profile)
    except RemoteStorage.DoesNotExist:
        storage = RemoteStorage(content_object=media, profile=profile)

    logger.info("Uploading %s to remote storage" % media)
    try:
        storage.upload(encode_path)
        storage.save()
    except Exception as exc:
        logger.info("Upload failed for %s, retrying" % media)
        raise self.retry(exc=exc, countdown=60)
    logger.info("Finished uploading %s to remote storage" % media)
