from __future__ import absolute_import

from django.core.exceptions import ObjectDoesNotExist

from celery import shared_task
from celery.utils.log import get_task_logger

from .models import EncodeProfile
from .models import Media
from .models import RemoteStorage


logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=5)
def encode_media(self, media_id, profile_id):
    """Encode a media file using a given ``EncodeProfile``."""
    try:
        media = Media.objects.get(pk=media_id)
        profile = EncodeProfile.objects.get(pk=profile_id)
    except ObjectDoesNotExist as exc:
        raise self.retry(exc=exc, countdown=5)

    logger.info("Encoding %s to %s" % (media, profile))
    try:
        encode_path = profile.encode(media)
    except Exception as exc:
        logger.info("Encoding failed for %s, retrying" % media)
        raise self.retry(exc=exc, countdown=60)
    logger.info("Finished encoding %s to %s" % (media, profile))
    return encode_path


@shared_task(bind=True, ignore_result=True, max_retries=3)
def upload_media(self, encode_path, media_id, profile_id):
    """Upload an encoded file to the configured remote storage."""
    try:
        media = Media.objects.get(pk=media_id)
        profile = EncodeProfile.objects.get(pk=profile_id)
    except ObjectDoesNotExist as exc:
        raise self.retry(exc=exc, countdown=5)
    try:
        storage = RemoteStorage.objects.get(media=media, profile=profile)
    except RemoteStorage.DoesNotExist:
        storage = RemoteStorage(media=media, profile=profile)

    logger.info("Uploading %s to remote storage" % media)
    try:
        storage.upload(encode_path)
        storage.save()
    except Exception as exc:
        logger.info("Upload failed for %s, retrying" % media)
        raise self.retry(exc=exc, countdown=60)
    logger.info("Finished uploading %s to remote storage" % media)

    media.set_active()


@shared_task(bind=True, ignore_result=True, max_retries=3)
def delete_media(self, storage_id):
    """Delete an encoded file from the configured remote storage."""
    try:
        storage = RemoteStorage.objects.get(pk=storage_id)
    except RemoteStorage.DoesNotExist as exc:
        raise self.retry(exc=exc, countdown=5)

    logger.info("Deleting %s from remote storage" % storage.remote_path)
    # Deleting the object first removes the remote media
    # file, and then deletes the object itself
    storage.delete()
