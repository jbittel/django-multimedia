from __future__ import unicode_literals

import logging
import os
import shlex
import subprocess
from tempfile import mkstemp

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from django.db.models.signals import m2m_changed
from django.db.models.signals import pre_save
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from celery import chain
from celery import chord

from .compat import user_model
from .signals import set_encode_profiles
from .signals import encode_profiles_changed
from .utils import import_by_path


logger = logging.getLogger(__name__)


def get_upload_path(instance, filename, absolute=False):
    """
    Build a unique path for uploaded media files.
    """
    relative_path = 'multimedia/%s/%s' % (instance.slug, filename)
    if absolute:
        return os.path.join(settings.MEDIA_ROOT, relative_path)
    else:
        return relative_path


@python_2_unicode_compatible
class EncodeProfile(models.Model):
    """
    Encoding profiles associated with ``MediaBase`` subclasses. Each
    media instance can have multiple encoding profiles associated
    with it. When a media instance is encoded, it will be encoded
    using all associated encoding profiles.
    """
    command = models.CharField(_('command'), max_length=1024)
    container = models.CharField(_('container'), max_length=32)
    name = models.CharField(_('name'), max_length=255)

    def __str__(self):
        return self.name

    def shell_command(self, input_path, output_path):
        """
        Interpolate paths into the given encoding command.
        """
        args = {'input': input_path, 'output': output_path}
        return shlex.split(self.command % args)

    def encode(self, media):
        """
        Encode media into a temporary file for the current
        encoding profile.
        """
        temp_file, encode_path = mkstemp(suffix=".%s" % self.container,
                                         dir=settings.FILE_UPLOAD_TEMP_DIR)
        command = self.shell_command(media.file.path, encode_path)
        try:
            subprocess.check_call(command, stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            logger.error("Encoding command returned %d while executing '%s'" %
                         (e.returncode, ' '.join(e.cmd)))
            raise
        except OSError:
            logger.error("Could not find encoding command '%s'" % command[0])
            raise
        return encode_path


@python_2_unicode_compatible
class RemoteStorage(models.Model):
    """
    Represents a specific encoded file that has been uploaded to the
    remote server.
    """
    content_type = models.ForeignKey(ContentType)
    media_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'media_id')
    profile = models.ForeignKey(EncodeProfile)
    created = models.DateTimeField(_('created'), editable=False)
    modified = models.DateTimeField(_('modified'), editable=False)

    def __str__(self):
        return self.remote_path

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = now()
        self.modified = now()
        super(RemoteStorage, self).save(*args, **kwargs)

    @property
    def remote_filename(self):
        """
        Return the remote filename from the associated media and profile.
        """
        return "%d%d.%s" % (self.media_id, self.profile_id,
                            self.profile.container)

    @property
    def remote_path(self):
        """
        Return the remote path from the associated media and profile.
        """
        return os.path.join(self.content_object.model_name, str(self.media_id),
                            self.remote_filename)

    def upload(self, local_path):
        """
        Upload a local file to remote storage, using the configured
        storage backend. If the upload succeeds, the file is deleted.
        """
        storage_class = getattr(settings, 'MULTIMEDIA_FILE_STORAGE', None)
        if storage_class is None:
            error = ('MULTIMEDIA_FILE_STORAGE must be specified in your '
                     'Django settings file')
            raise ImproperlyConfigured(error)

        remote_storage = import_by_path(storage_class)()
        try:
            logger.info("Uploading %s to %s" % (local_path, self.remote_path))
            remote_storage.save(self.remote_path, open(local_path))
        except Exception:
            logger.error("Error saving '%s' to remote storage" % local_path)
            raise
        try:
            os.unlink(local_path)
        except OSError as e:
            logger.error("Error removing temporary file '%s': %s" % (local_path, e))


class MediaManager(models.Manager):
    def by_container(self, containers):
        """
        Return a queryset with media files that have been encoded into
        one of the given set of containers. Containers should be
        specified as a list of strings.
        """
        return self.filter(storage__profile__container__in=containers)

    def by_profile(self, profiles=[]):
        """
        Return a queryset with media files that have been encoded into
        one of the given set of ``EncodeProfile``s. Profiles should be
        specified as a list of ``EncodeProfile`` instances.
        """
        return self.filter(storage__profile__in=profiles)


@python_2_unicode_compatible
class MediaBase(models.Model):
    """
    An abstract base class implementing common fields and methods for
    individual media type subclasses.
    """
    title = models.CharField(_('title'), max_length=255)
    slug = models.SlugField(_('slug'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    created = models.DateTimeField(_('created'), editable=False)
    modified = models.DateTimeField(_('modified'), editable=False)
    owner = models.ForeignKey(user_model, verbose_name=_('owner'), editable=False)
    profiles = models.ManyToManyField(EncodeProfile)
    storage = generic.GenericRelation(RemoteStorage, object_id_field='media_id')
    file = models.FileField(_('file'), upload_to=get_upload_path)

    objects = MediaManager()

    class Meta:
        abstract = True
        ordering = ('-created',)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = now()
        self.modified = now()
        super(MediaBase, self).save(*args, **kwargs)

    @property
    def model_name(self):
        return self.__class__.__name__.lower()

    def encode(self, profiles=[]):
        """
        Encode media with the specified ``EncodeProfile``s using
        asynchronous Celery tasks. The media is encoded into a
        temporary directory and then uploaded to the configured media
        server.

        If ``profiles`` is specified, encode with that list of
        ``EncodeProfile`` primary keys; otherwise, encode with all
        associated ``EncodeProfile``s.
        """
        from .tasks import encode_media, upload_media, encode_complete

        if not profiles:
            profiles = list(self.profiles.values_list('pk', flat=True))

        group = []
        for profile_id in profiles:
            group.append(chain(encode_media.s(self.model_name, self.id, profile_id),
                               upload_media.s(self.model_name, self.id, profile_id)))
        chord((group), encode_complete.si(self.model_name, self.id)).apply_async()


class Video(MediaBase):
    class Meta:
        verbose_name = "Video File"
        verbose_name_plural = "Video Files"


class Audio(MediaBase):
    class Meta:
        verbose_name = "Audio File"
        verbose_name_plural = "Audio Files"


pre_save.connect(set_encode_profiles, sender=Video)
pre_save.connect(set_encode_profiles, sender=Audio)
m2m_changed.connect(encode_profiles_changed, sender=MediaBase.profiles.through)
