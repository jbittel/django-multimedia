from __future__ import unicode_literals

import os
import paramiko
import shlex
import subprocess

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.db.models.signals import m2m_changed
from django.db.models.signals import pre_save
from django.template.loader import render_to_string
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:  # Django version < 1.5
    from django.contrib.auth.models import User

from celery import chord

from filer.fields.image import FilerImageField

from .signals import check_file_changed
from .signals import thumbnail_offset_changed
from .signals import encode_on_change
from .storage import OverwritingStorage
from .conf import multimedia_settings


def multimedia_path(instance, filename, absolute=False):
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
        args = {'input': input_path, 'output': output_path}
        return shlex.split(self.command % args)


@python_2_unicode_compatible
class MediaBase(models.Model):
    """
    """
    title = models.CharField(_('title'), max_length=255)
    slug = models.SlugField(_('slug'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    created = models.DateTimeField(_('created'), editable=False)
    modified = models.DateTimeField(_('modified'), editable=False)
    owner = models.ForeignKey(User, verbose_name=_('owner'), editable=False)
    profiles = models.ManyToManyField(EncodeProfile)

    file = models.FileField(_('file'), upload_to=multimedia_path)
    encoding = models.BooleanField(_('encoding'), default=False, editable=False,
                                   help_text="Indicates this file is currently encoding")
    encoded = models.BooleanField(_('encoded'), default=False, editable=False,
                                  help_text="Indicates this file has finished encoding")
    uploaded = models.BooleanField(_('uploaded'), default=False, editable=False,
                                   help_text="Indicates this file has been uploaded")

    class Meta:
        abstract = True
        ordering = ('-created',)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = now()
        self.modified = now()
        if not self.encoded:
            self.encoding = True
            self.uploaded = False
        super(MediaBase, self).save(*args, **kwargs)

    def encode(self):
        """
        Encode a ``MediaBase`` subclass using all associated
        ``EncodeProfile``s using a group of Celery tasks.
        """
        from .tasks import encode_media, encode_media_complete
        model = self.__class__.__name__.lower()
        chord((encode_media.s(model, self.id, p.id) for p in self.profiles.all()),
              encode_media_complete.si(model, self.id)).apply_async(countdown=5)

    def container_path(self, profile):
        return multimedia_path(self, "%s.%s" % (self.id, profile.container), absolute=True)

    def encode_to_container(self, profile):
        """
        Encode a ``MediaBase`` subclass using the given profile
        into the given profile's container.
        """
        subprocess.check_call(profile.shell_command(self.file.path,
                                                    self.container_path(profile)),
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def upload_to_server(self, profile):
        """
        Upload an encoded file to a remote media server.
        """
        remote_path = os.path.join(multimedia_settings.MEDIA_SERVER_VIDEO_PATH,
                                   "%s.%s" % (self.id, profile.container))
        transport = paramiko.Transport((multimedia_settings.MEDIA_SERVER_HOST,
                                        multimedia_settings.MEDIA_SERVER_PORT))
        transport.connect(username=multimedia_settings.MEDIA_SERVER_USER,
                          password=multimedia_settings.MEDIA_SERVER_PASSWORD)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(self.container_path(profile), remote_path)
        sftp.close()
        transport.close()


class Video(MediaBase):
    auto_thumbnail = models.FileField(upload_to=multimedia_path,
                                      null=True, blank=True, editable=False,
                                      storage=OverwritingStorage())
    auto_thumbnail_offset = models.PositiveIntegerField(blank=True, default=4,
                                                        help_text="Offset for automatic thumbnail, in seconds")
    custom_thumbnail = FilerImageField(blank=True, null=True,
                                       help_text="Upload a custom thumbnail image")

    class Meta:
        verbose_name = "Video File"
        verbose_name_plural = "Video Files"

    def save(self, *args, **kwargs):
        from .tasks import generate_thumbnail
        super(Video, self).save(*args, **kwargs)
        if not self.auto_thumbnail:
            model = self.__class__.__name__.lower()
            generate_thumbnail.apply_async((model, self.id), countdown=5)

    @property
    def thumbnail(self):
        if self.custom_thumbnail:
            return self.custom_thumbnail
        else:
            return self.auto_thumbnail

    def thumbnail_html(self):
        return render_to_string('multimedia/thumbnail.html', {'img': self.thumbnail,
                                                              'alt': self.title})
    thumbnail_html.allow_tags = True
    thumbnail_html.short_description = 'Thumbnail'

    def generate_thumbnail(self):
        command = multimedia_settings.MULTIMEDIA_THUMBNAIL_CMD
        filename = "%s.jpg" % self.id
        output_path = multimedia_path(self, filename, absolute=True)
        args = {'input': self.file.path,
                'output': output_path,
                'offset': self.auto_thumbnail_offset}
        shell_command = shlex.split(command % args)
        subprocess.check_call(shell_command,
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        f = open(output_path)
        self.auto_thumbnail.save(filename,
                                 SimpleUploadedFile(filename, f.read(),
                                                    content_type="image/jpg"),
                                 save=False)
        self.save()
        f.close()


class Audio(MediaBase):
    class Meta:
        verbose_name = "Audio File"
        verbose_name_plural = "Audio Files"


pre_save.connect(check_file_changed, sender=MediaBase)
pre_save.connect(thumbnail_offset_changed, sender=Video)
m2m_changed.connect(encode_on_change, sender=MediaBase.profiles.through)
