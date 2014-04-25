from __future__ import unicode_literals

import logging
import os
import shlex
import subprocess
from tempfile import mkstemp

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models.signals import m2m_changed
from django.db.models.signals import pre_save
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from .compat import user_model
from .signals import set_encode_profiles
from .signals import encode_profiles_changed
from .utils import import_by_path


logger = logging.getLogger(__name__)


DEFAULT_FILE_TYPE_CHOICES = (
    ('audio', 'Audio'),
    ('video', 'Video'),
    ('image', 'Image'),
)


@python_2_unicode_compatible
class EncodeProfile(models.Model):
    """Encoding profiles associated with ``Media``.

    Each ``EncodeProfile`` specifies a command line statement that
    performs the encoding. Multiple ``EncodeProfile``s may be
    associated with ``Media`` to output multiple encodings.
    """
    command = models.CharField(_('command'), max_length=1024)
    container = models.CharField(_('container'), max_length=32)
    name = models.CharField(_('name'), max_length=255)
    file_type = models.CharField(_('type'), max_length=32,
                                 choices=DEFAULT_FILE_TYPE_CHOICES)

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
    """An encoded file that has been uploaded to a remote server."""
    media = models.ForeignKey('Media')
    profile = models.ForeignKey(EncodeProfile)
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField(editable=False)

    def __str__(self):
        return self.remote_path

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = now()
        self.modified = now()
        super(RemoteStorage, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.unlink()
        super(RemoteStorage, self).delete(*args, **kwargs)

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
        return os.path.join(self.profile.file_type, str(self.media_id),
                            self.remote_filename)

    def get_storage(self):
        """
        Return an instance of the currently configured storage class.
        If ``MULTIMEDIA_FILE_STORAGE`` is not defined or there is an
        error importing the module, ``ImproperlyConfigured`` is raised.
        """
        if hasattr(self, '_storage'):
            return self._storage
        storage_class = getattr(settings, 'MULTIMEDIA_FILE_STORAGE', None)
        if storage_class is None:
            error = ('MULTIMEDIA_FILE_STORAGE must be specified in your '
                     'Django settings file')
            raise ImproperlyConfigured(error)
        self._storage = import_by_path(storage_class)()
        return self._storage

    def upload(self, local_path):
        """
        Upload a local file to remote storage, using the configured
        storage backend. If the upload succeeds, the file is deleted.
        """
        try:
            if self.exists():
                self.unlink()
            logger.info("Uploading %s to %s" % (local_path, self.remote_path))
            self.get_storage().save(self.remote_path, open(local_path))
        except Exception:
            logger.error("Error saving '%s' to remote storage" % local_path)
            raise
        try:
            os.unlink(local_path)
        except OSError as e:
            logger.error("Error removing temporary file '%s': %s" % (local_path, e))

    def exists(self):
        """
        Return True if the remote file exists, or False otherwise.
        """
        return self.get_storage().exists(self.remote_path)

    def unlink(self):
        """
        Delete the remote file, if it exists.
        """
        logger.info("Deleting %s" % self.remote_path)
        try:
            self.get_storage().delete(self.remote_path)
        except IOError:
            pass


def media_upload_to(instance, filename):
    """Return a unique path for uploaded media files."""
    return 'multimedia/%s/%s' % (instance.slug, filename)


class MediaManager(models.Manager):
    def by_container(self, containers):
        """
        Return a queryset with media files that have been encoded into
        one of the given set of containers. Containers should be
        specified as a list of strings.
        """
        return self.filter(remotestorage__profile__container__in=containers)

    def by_profile(self, profiles=[]):
        """
        Return a queryset with media files that have been encoded into
        one of the given set of ``EncodeProfile``s. Profiles should be
        specified as a list of ``EncodeProfile`` instances.
        """
        return self.filter(remotestorage__profile__in=profiles)

    def by_type(self, type=None):
        """
        Return a queryset with ``Media`` that has been encoded into
        the given file type.
        """
        return self.filter(remotestorage__profile__file_type=type).distinct()


@python_2_unicode_compatible
class Media(models.Model):
    """
    """
    title = models.CharField(_('title'), max_length=255)
    slug = models.SlugField(_('slug'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    created = models.DateTimeField(_('created'), editable=False)
    modified = models.DateTimeField(_('modified'), editable=False)
    owner = models.ForeignKey(user_model, verbose_name=_('owner'), editable=False)
    profiles = models.ManyToManyField(EncodeProfile)
    file = models.FileField(_('file'), upload_to=media_upload_to)

    objects = MediaManager()

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Media'
        verbose_name_plural = 'Media'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = now()
        self.modified = now()
        super(Media, self).save(*args, **kwargs)

    def encode(self, profiles=[]):
        """
        Encode and upload media using asynchronous Celery tasks. If
        ``profiles`` are specified, encode with that list of
        ``EncodeProfile`` primary keys; otherwise, encode with all
        associated ``EncodeProfile``s.
        """
        from .tasks import encode_media, upload_media

        if not profiles:
            profiles = list(self.profiles.values_list('pk', flat=True))

        for profile_id in profiles:
            (encode_media.s(self.id, profile_id) |
             upload_media.s(self.id, profile_id)).apply_async()


pre_save.connect(set_encode_profiles, sender=Media)
m2m_changed.connect(encode_profiles_changed, sender=Media.profiles.through)
