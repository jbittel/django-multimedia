from __future__ import unicode_literals

from filecmp import cmp
import os
import paramiko
import shlex
import subprocess

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:  # Django version < 1.5
    from django.contrib.auth.models import User

from filer.fields.image import FilerImageField

from .storage import OverwritingStorage
from .conf import multimedia_settings


@receiver(pre_save)
def check_file_changed(sender, instance, **kwargs):
    if instance.id and hasattr(instance.file.file, "temporary_file_path"):
        current = sender.objects.get(pk=instance.id)
        if not cmp(os.path.join(settings.MEDIA_ROOT, current.file.name),
                   os.path.join(settings.MEDIA_ROOT, instance.file.file.temporary_file_path())):
            instance.uploaded = False
            instance.encoded = False
            instance.encoding = True
        current.file.delete(save=False)


def local_path(instance, filename, absolute=False):
    relative_path = 'multimedia/%s/%s' % (instance.slug, filename)
    if absolute:
        return os.path.join(settings.MEDIA_ROOT, relative_path)
    else:
        return relative_path


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

    file = models.FileField(_('file'), upload_to=local_path)
    encoding = models.BooleanField(_('encoding'), default=False, editable=False,
                                   help_text="Indicates this file is currently encoding")
    encoded = models.BooleanField(_('encoded'), default=False, editable=False,
                                  help_text="Indicates this file has finished encoding")
    uploaded = models.BooleanField(_('uploaded'), default=False, editable=False,
                                   help_text="Indicates this file has been uploaded")

    class Meta:
        ordering = ('-created',)
        verbose_name = "Media File"
        verbose_name_plural = "Media Files"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = now()
        self.modified = now()
        super(MediaBase, self).save(*args, **kwargs)

    def output_path(self, profile):
        raise NotImplementedError('subclasses of MediaBase must provide an output_path() method')

    def encode_cmd(self, profile):
        raise NotImplementedError('subclasses of MediaBase must provide an encode_cmd() method')

    def encode(self, profile):
        command = shlex.split(self.encode_cmd(profile))
        process = subprocess.call(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.encoded = True
        self.encoding = False
        self.save()

    def get_remote_path(self, path):
        filename = os.path.basename(path)
        return os.path.join(multimedia_settings.MEDIA_SERVER_VIDEO_PATH, filename)

    def notify_owner(self):
        from_email = multimedia_settings.MULTIMEDIA_NOTIFICATION_EMAIL
        subject = "Multimedia Uploaded (%s)" % self.title
        message = render_to_string("multimedia/email_notification.txt", {"media": self})
        self.owner.email_user(subject, message, from_email=from_email)

    def upload_file(self, path):
        remote_path = self.get_remote_path(path)
        transport = paramiko.Transport((multimedia_settings.MEDIA_SERVER_HOST,
                                        multimedia_settings.MEDIA_SERVER_PORT))
        transport.connect(username=multimedia_settings.MEDIA_SERVER_USER,
                          password=multimedia_settings.MEDIA_SERVER_PASSWORD)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(path, remote_path)
        sftp.close()
        transport.close()
        self.uploaded = True
        self.save()


class Video(MediaBase):
    auto_thumbnail = models.FileField(upload_to=local_path,
                                      null=True, blank=True, editable=False,
                                      storage=OverwritingStorage())
    auto_thumbnail_offset = models.PositiveIntegerField(blank=True, default=4,
                                                        help_text="Offset for automatic thumbnail, in seconds")
    custom_thumbnail = FilerImageField(blank=True, null=True,
                                       help_text="Upload a custom thumbnail image")

    class Meta:
        verbose_name = "Video File"
        verbose_name_plural = "Video Files"

    def output_path(self, profile):
        container = multimedia_settings.MULTIMEDIA_VIDEO_PROFILES[profile].get('container')
        return local_path(self, "%s.%s" % (self.id, container), absolute=True)

    def encode_cmd(self, profile):
        cmd = multimedia_settings.MULTIMEDIA_VIDEO_PROFILES[profile].get("encode")
        args = {"input": self.file.path, "output": self.output_path(profile)}
        return cmd % args

    @property
    def thumbnail(self):
        if self.custom_thumbnail:
            return self.custom_thumbnail
        else:
            return self.auto_thumbnail

    def admin_thumbnail(self):
        return render_to_string("multimedia/screenshot_admin.html", {"img": self.thumbnail})
    admin_thumbnail.allow_tags = True
    admin_thumbnail.short_description = "Thumbnail"

    @property
    def thumbnail_cmd(self):
        cmd = multimedia_settings.MULTIMEDIA_THUMBNAIL_CMD
        output_path = local_path(self, "%s.jpg" % self.id, absolute=True)
        args = {"input": self.file.path, "offset": self.auto_thumbnail_offset, "output": output_path}
        return cmd % args

    def make_thumbnail(self):
        cmd = shlex.split(self.thumbnail_cmd)
        process = subprocess.call(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        f = open(local_path(self, "%s.jpg" % self.id, absolute=True))
        self.auto_thumbnail.save("%s.jpg" % self.id,
                                 SimpleUploadedFile("%s.jpg" % self.id, f.read(), content_type="image/jpg"),
                                 save=False)
        self.save()
        f.close()

    def save(self, *args, **kwargs):
        from .tasks import encode_upload_video
        if not self.encoded:
            self.encoding = True
            self.uploaded = False
        super(Video, self).save(*args, **kwargs)
        if not self.encoded:
            encode_upload_video(self.id)


class Audio(MediaBase):
    class Meta:
        verbose_name = "Audio File"
        verbose_name_plural = "Audio Files"

    def save(self, *args, **kwargs):
#        from tasks import encode_media, upload_media
        super(Audio, self).save(*args, **kwargs)
#        if not self.encoded:
#            encode_media.delay(self.id, callback=subtask(upload_media))

    def output_path(self, profile):
        container = multimedia_settings.MULTIMEDIA_AUDIO_PROFILES[profile].get('container')
        return local_path(self, "%s.%s" % (self.id, container), absolute=True)

    def encode_cmd(self, profile):
        cmd = multimedia_settings.MULTIMEDIA_AUDIO_PROFILES[profile].get("encode")
        args = {"input": self.file.path, "output": self.output_path(profile)}
        return cmd % args
