from celery.decorators import task
from celery.task.sets import subtask

import os
import shutil
import shlex
import subprocess
from dateutil import parser
from django.utils.html import strip_tags
from django.conf import settings
from django.core.files import File

from models import MediaBase, Video, Audio

@task(max_retries=3)
def generate_thumbnail(video_id, callback=None):
    media = Video.objects.get(pk=video_id)
    logger = generate_thumbnail.get_logger()
    logger.info("Generating thumbnail for %s" % media)
    try:
        media.make_thumbnail()
    except Exception, exc:
        logger.info("Generate thumbnail failed for %s - retrying " % media)
        generate_thumbnail.retry(exc=exc, countdown=60)
    logger.info("Done generating thumbnail for %s" % media)
    if callback:
        subtask(callback).delay(media.id)

@task(max_retries=3)
def encode_media(media_id, callback=None):
    base = MediaBase.objects.get(pk=media_id)
    media = base.get_media()
    logger = encode_media.get_logger()
    logger.info("Encoding %s" % media)
    try:
        media.encode_file()
    except Exception, exc:
        logger.info("Encode Media failed for %s - retrying " % media)
        encode_media.retry(exc=exc, countdown=60)
    logger.info("Done encoding for %s" % media)
    logger.info("Saving model and starting upload for %s" % media)
    if callback:
        subtask(callback).delay(media.id)
    
@task(max_retries=3)
def upload_media(media_id):
    base = MediaBase.objects.get(pk=media_id)
    media = base.get_media()
    logger = upload_media.get_logger()
    logger.info("Uploading encoded file for %s" % media)
    try:    
        media.upload_file()
    except Exception, exc:
        logger.info("Upload media failed for %s - retrying " % media)
        upload_media.retry(exc=exc, countdown=60)
    logger.info("Upload complete for %s" % media)
        
