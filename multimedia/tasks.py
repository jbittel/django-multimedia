from django.contrib.contenttypes.models import ContentType

from celery import chain
from celery import chord
from celery.decorators import task
from celery.utils.log import get_task_logger

from conf import multimedia_settings


logger = get_task_logger(__name__)


def encode_upload_video(video_id):
    """
    """
    group = []
    for profile in multimedia_settings.MULTIMEDIA_VIDEO_PROFILES:
        group.append(chain(encode_media.s(profile, 'video', video_id),
                           upload_media.s('video', video_id)))
    group.append(generate_thumbnail.si('video', video_id))
    chord((group), notify_owner.si('video', video_id)).apply_async(countdown=10)


@task(max_retries=3)
def encode_media(profile, model, media_id):
    media_type = ContentType.objects.get(app_label='multimedia', model=model)
    media = media_type.get_object_for_this_type(pk=media_id)
    if not media.encoded:
        logger.info("Encoding %s" % media)
        try:
            media.encode(profile)
        except Exception as exc:
            logger.info("Encoding failed for %s, retrying" % media)
            raise encode_media.retry(exc=exc, countdown=60)
        logger.info("Done encoding for %s" % media)
    return media.output_path(profile)


@task(max_retries=3)
def upload_media(path, model, media_id):
    media_type = ContentType.objects.get(app_label='multimedia', model=model)
    media = media_type.get_object_for_this_type(pk=media_id)
    if not media.uploaded:
        logger.info("Uploading encoded file for %s" % media)
        try:
            media.upload_file(path)
        except Exception as exc:
            logger.info("Upload failed for %s, retrying" % media)
            raise upload_media.retry(exc=exc, countdown=60)
        logger.info("Upload complete for %s" % media)


@task(max_retries=3)
def generate_thumbnail(model, media_id):
    media_type = ContentType.objects.get(app_label='multimedia', model=model)
    media = media_type.get_object_for_this_type(pk=media_id)
    logger.info("Generating thumbnail for %s" % media)
    try:
        media.make_thumbnail()
    except Exception as exc:
        logger.info("Thumbnail generation failed for %s, retrying" % media)
        raise generate_thumbnail.retry(exc=exc, countdown=60)
    logger.info("Done generating thumbnail for %s" % media)


@task(max_retries=3)
def notify_owner(model, media_id):
    media_type = ContentType.objects.get(app_label='multimedia', model=model)
    media = media_type.get_object_for_this_type(pk=media_id)
    media.notify_owner()
