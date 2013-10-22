from celery import chain
from celery import chord
from celery.decorators import task
from celery.utils.log import get_task_logger

from models import Video

from conf import multimedia_settings


logger = get_task_logger(__name__)


def encode_upload_video(video_id):
    """
    """
    group = []
    for profile in multimedia_settings.MULTIMEDIA_VIDEO_PROFILES:
        group.append(chain(encode_video.s(profile, video_id),
                           upload_video.s(video_id)))
    group.append(generate_thumbnail.s(video_id))
    chord((group), notify_owner.si(video_id)).apply_async(countdown=10)


@task(max_retries=3)
def encode_video(profile, video_id):
    video = Video.objects.get(pk=video_id)
    if not video.encoded:
        logger.info("Encoding %s" % video)
        try:
            video.encode(profile)
        except Exception as exc:
            logger.info("Encoding failed for %s, retrying" % video)
            raise encode_video.retry(exc=exc, countdown=60)
        logger.info("Done encoding for %s" % video)
    return video.output_path(profile)


@task(max_retries=3)
def upload_video(path, video_id):
    video = Video.objects.get(pk=video_id)
    if not video.uploaded:
        logger.info("Uploading encoded file for %s" % video)
        try:
            video.upload_file(path)
        except Exception as exc:
            logger.info("Upload failed for %s, retrying" % video)
            raise upload_video.retry(exc=exc, countdown=60)
        logger.info("Upload complete for %s" % video)


@task(max_retries=3)
def generate_thumbnail(video_id):
    video = Video.objects.get(pk=video_id)
    logger.info("Generating thumbnail for %s" % video)
    try:
        video.make_thumbnail()
    except Exception as exc:
        logger.info("Thumbnail generation failed for %s, retrying" % video)
        raise generate_thumbnail.retry(exc=exc, countdown=60)
    logger.info("Done generating thumbnail for %s" % video)


@task(max_retries=3)
def notify_owner(video_id):
    video = Video.objects.get(pk=video_id)
    video.notify_owner()
