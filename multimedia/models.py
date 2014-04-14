from __future__ import unicode_literals

import os
import shlex
import subprocess
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.db.models.signals import m2m_changed
from django.db.models.signals import pre_save
from django.template.loader import render_to_string
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from celery import chain
from celery import chord
from filer.fields.image import FilerImageField

from .compat import user_model
from .conf import multimedia_settings
from .signals import set_encode_profiles
from .signals import encode_profiles_changed
from .signals import thumbnail_offset_changed
from .storage import OverwritingStorage


def multimedia_path(instance, filename, absolute=False):
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

    def encode(self, media, output_dir):
        """
        Encode media into a temporary directory for the current
        encoding profile.
        """
        encode_path = os.path.join(output_dir, "%d%d.%s" % (media.id, self.id,
                                                            self.container))
        subprocess.check_call(self.shell_command(media.file.path, encode_path),
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        return encode_path


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

    file = models.FileField(_('file'), upload_to=multimedia_path)
    encoding = models.BooleanField(_('encoding'), default=False, editable=False,
                                   help_text="Indicates this file is currently encoding")
    encoded = models.BooleanField(_('encoded'), default=False, editable=False,
                                  help_text="Indicates this file has finished encoding")

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
        from .tasks import encode_media, upload_media, encode_media_complete

        self.encoding = True
        self.save()

        if not profiles:
            profiles = list(self.profiles.values_list('pk', flat=True))

        tmpdir = tempfile.mkdtemp()
        group = []
        for profile_id in profiles:
            group.append(chain(encode_media.s(self.model_name, self.id,
                                              profile_id, tmpdir),
                               upload_media.s(self.model_name, self.id)))
        chord((group), encode_media_complete.si(self.model_name, self.id,
                                                tmpdir)).apply_async(countdown=5)


class Video(MediaBase):
    auto_thumbnail = models.ImageField(upload_to=multimedia_path,
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
        created = self.pk is None
        super(Video, self).save(*args, **kwargs)
        if created:
            generate_thumbnail.apply_async((self.model_name, self.pk),
                                           countdown=5)

    @property
    def thumbnail(self):
        if self.custom_thumbnail:
            return self.custom_thumbnail
        else:
            return self.auto_thumbnail

    def thumbnail_html(self):
        return render_to_string('multimedia/thumbnail.html',
                                {'img': self.thumbnail, 'alt': self.title})
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
                                                    content_type="image/jpg"))
        f.close()


class Audio(MediaBase):
    class Meta:
        verbose_name = "Audio File"
        verbose_name_plural = "Audio Files"


pre_save.connect(set_encode_profiles, sender=Video)
pre_save.connect(set_encode_profiles, sender=Audio)
pre_save.connect(thumbnail_offset_changed, sender=Video)
m2m_changed.connect(encode_profiles_changed, sender=MediaBase.profiles.through)
