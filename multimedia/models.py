from __future__ import unicode_literals

import hashlib
import logging
import os
import shlex
import subprocess
from tempfile import mkstemp

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files import File
from django.db import models
from django.db.models.signals import m2m_changed
from django.db.models.signals import pre_delete
from django.db.models.signals import pre_save
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from .compat import user_model
from .signals import set_encode_profiles
from .signals import encode_profiles_changed
from .signals import delete_remote_storage
from .utils import get_callable


logger = logging.getLogger(__name__)


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
        os.close(temp_file)
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
    An encoded file stored on a remote server, uploaded using the
    configured storage backend.
    """
    media = models.ForeignKey('Media', blank=True, null=True, on_delete=models.SET_NULL)
    profile = models.ForeignKey(EncodeProfile, on_delete=models.PROTECT)
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField(editable=False)
    content_hash = models.CharField(max_length=64)

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
    def remote_path(self):
        """Build the remote file path from the content hash."""
        filename = "%s.%s" % (self.content_hash, self.profile.container)
        return os.path.join(self.content_hash[0:1], self.content_hash[0:2],
                            filename)

    def generate_content_hash(self, path, chunk_size=None):
        """Return a SHA1 hash of the file's contents."""
        if not chunk_size:
            chunk_size = File.DEFAULT_CHUNK_SIZE

        sha1 = hashlib.sha1()
        with open(path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                sha1.update(chunk)
        return sha1.hexdigest()

    def get_absolute_url(self, **kwargs):
        return self.get_storage().url(self.remote_path, **kwargs)

    def get_storage(self):
        """Return an instance of the currently configured storage class."""
        if hasattr(self, '_storage'):
            return self._storage
        storage_class = getattr(settings, 'MULTIMEDIA_FILE_STORAGE', None)
        if storage_class is None:
            error = ('MULTIMEDIA_FILE_STORAGE must be specified in your '
                     'Django settings file')
            raise ImproperlyConfigured(error)
        self._storage = get_callable(storage_class)()
        return self._storage

    def upload(self, local_path):
        """
        Upload an encoded file to remote storage and remove the
        local file.
        """
        new_hash = self.generate_content_hash(local_path)
        if new_hash != self.content_hash:
            self.unlink()
            self.content_hash = new_hash

        if not self.exists():
            try:
                logger.info("Uploading %s to %s" % (local_path, self.remote_path))
                self.get_storage().save(self.remote_path, open(local_path))
            except Exception as e:
                logger.error("Error saving '%s' to remote storage: %s" % (local_path, e))
                raise
        try:
            os.unlink(local_path)
        except OSError as e:
            logger.error("Error removing file '%s': %s" % (local_path, e))

    def exists(self):
        """Return True if the remote file exists, or False otherwise."""
        return self.get_storage().exists(self.remote_path)

    def unlink(self):
        """Delete the remote file if it is no longer referenced."""
        refs = RemoteStorage.objects.filter(content_hash=self.content_hash)
        if refs.count() == 1:
            try:
                logger.info("Deleting %s" % self.remote_path)
                self.get_storage().delete(self.remote_path)
            except IOError as e:
                logger.error("Error removing file '%s': %s" %
                             (self.remote_path, e))


class MediaManager(models.Manager):
    def active(self):
        """
        Return a queryset with media files that have been encoded into
        all of their initially associated encoding profiles.
        """
        return self.filter(active=True)

    def by_container(self, containers):
        """
        Return a queryset with media files that have been encoded into
        one of the given set of containers. Containers should be
        specified as a list of strings.
        """
        return self.filter(remotestorage__profile__container__in=containers).distinct()

    def by_profile(self, profiles):
        """
        Return a queryset with media files that have been encoded into
        one of the given set of ``EncodeProfile``s. Profiles should be
        specified as a list of ``EncodeProfile`` instances.
        """
        return self.filter(remotestorage__profile__in=profiles).distinct()


@python_2_unicode_compatible
class Media(models.Model):
    """A media file to be encoded and uploaded to a remote server."""
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    created = models.DateTimeField(_('created'), editable=False)
    modified = models.DateTimeField(_('modified'), editable=False)
    owner = models.ForeignKey(user_model, verbose_name=_('owner'), editable=False)
    profiles = models.ManyToManyField(EncodeProfile)
    file = models.FileField(_('file'), upload_to='multimedia/%Y/%m/%d')
    active = models.BooleanField(default=False, editable=False)

    objects = MediaManager()

    class Meta:
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

    def set_active(self):
        """
        Set the media as active when it has been encoded into all
        associated ``EncodeProfile``s. Currently this is a one-way
        transition to prevent media from dropping in and out of the
        active set.
        """
        if not self.active:
            storage_keys = set(self.remotestorage_set.values_list('profile', flat=True))
            profile_keys = set(self.profiles.values_list('pk', flat=True))
            if storage_keys == profile_keys:
                self.active = True
                self.save()


pre_save.connect(set_encode_profiles, sender=Media)
m2m_changed.connect(encode_profiles_changed, sender=Media.profiles.through)
pre_delete.connect(delete_remote_storage, sender=Media)
