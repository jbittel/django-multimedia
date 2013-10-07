from celery.decorators import task
from celery.task.sets import subtask
from celery.utils.log import get_task_logger

from models import MediaBase, Video


logger = get_task_logger(__name__)


@task(max_retries=3)
def generate_thumbnail(video_id):
    media = Video.objects.get(pk=video_id)
    logger.info("Generating thumbnail for %s" % media)
    try:
        media.make_thumbnail()
    except Exception as exc:
        logger.info("Generate thumbnail failed for %s - retrying " % media)
        raise generate_thumbnail.retry(exc=exc, countdown=60)
    logger.info("Done generating thumbnail for %s" % media)


@task(max_retries=3)
def encode_media(media_id, callback=None):
    base = MediaBase.objects.get(pk=media_id)
    media = base.get_media()
    logger.info("Encoding %s" % media)
    try:
        media.encode_file()
    except Exception as exc:
        logger.info("Encode Media failed for %s - retrying " % media)
        raise encode_media.retry(exc=exc, countdown=60)
    logger.info("Done encoding for %s" % media)
    logger.info("Saving model and starting upload for %s" % media)
    if callback:
        subtask(callback).delay(media.id)


@task(max_retries=3)
def upload_media(media_id):
    base = MediaBase.objects.get(pk=media_id)
    media = base.get_media()
    logger.info("Uploading encoded file for %s" % media)
    try:
        media.upload_file()
    except Exception as exc:
        logger.info("Upload media failed for %s - retrying " % media)
        raise upload_media.retry(exc=exc, countdown=60)
    logger.info("Upload complete for %s" % media)
