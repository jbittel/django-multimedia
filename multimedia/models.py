import os
import paramiko
import shlex
import subprocess

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User
from filer.fields.image import FilerImageField
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMessage
from django.core.files import File

from celery.task.sets import subtask

from django.core.files.uploadedfile import SimpleUploadedFile

from storage import OverwritingStorage
from conf import multimedia_settings


VIDEO_PROFILES = [ (k, v.get("name",k)) for k,v in multimedia_settings.MULTIMEDIA_VIDEO_PROFILES.iteritems()]
AUDIO_PROFILES = [ (k, v.get("name",k)) for k,v in multimedia_settings.MULTIMEDIA_AUDIO_PROFILES.iteritems()]

FILE_TYPES = (    
    ("audio","audio"),
    ("video","video"),
)

class MediaManager(models.Manager):
    def active(self):
        return self.filter(uploaded=True, encoded=True)

def get_media_upload_to(instance,filename):
        return u'multimedia/%s/%s/%s' %  (instance.file_type, instance.slug, filename)

class MediaBase(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    date_added = models.DateField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to=get_media_upload_to)
    uploaded = models.BooleanField(default=False, editable=False, help_text="Indicates that this file has been uploaded to a streaming server")
    user = models.ForeignKey(User, null=True, help_text="The user who uploaded the file")
    file_type = models.CharField(max_length=255, choices=FILE_TYPES)
    profile = models.CharField(max_length=255)
    encoded = models.BooleanField(default=False, editable=False, help_text="Indicates that this file has finished encoding")
    encoding = models.BooleanField(default=False, editable=False, help_text="Indicates that this file is currently encoding")
    objects = MediaManager()
    
    def get_profile(self):
        return None
    
    @property
    def container(self):
        return self.get_profile().get("container","media")
    
    @property
    def encode(self):
        return self.get_profile().get("encode",False)
    
    @property
    def encode_cmd(self):
        encode_cmd = self.get_profile().get("encode_cmd")
        input_path = os.path.join(settings.MEDIA_ROOT, self.file.name)
        args = {"input":input_path, "output":self.output_path}
        return str(encode_cmd % args)
    
    @property
    def output_path(self):
        encode = self.get_profile().get("encode",False)
        if encode:
            return os.path.join(settings.MEDIA_ROOT, "multimedia/%s/%s/%s.%s" % (self.file_type, self.slug, self.id, self.container))
        else:
            return os.path.join(settings.MEDIA_ROOT, self.file.name)
    
    def encode_file(self):
        command = shlex.split(self.encode_cmd)
        process = subprocess.call(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.encoded = True
        self.encoding = False
        self.save()
    
    def get_media(self):
        return self.video if self.file_type == "video" else self.audio
           
    def get_remote_path(self):
        return None
        
    def notify_user(self):
        from_email = multimedia_settings.MULTIMEDIA_NOTIFICATION_EMAIL
        to_email = [str(self.user.email),]
        subject = "Multimedia Uploaded (%s)" % self.title
        message = render_to_string("multimedia/email_notification.txt", {"media":self})
        send_mail(subject, message, from_email, to_email, fail_silently=True)
    
    def upload_file(self):
        local_file_path = self.output_path
        remote_file_path = self.get_remote_path()

        transport = paramiko.Transport((multimedia_settings.MEDIA_SERVER_HOST, multimedia_settings.MEDIA_SERVER_PORT))
        transport.connect(username=multimedia_settings.MEDIA_SERVER_USER, password=multimedia_settings.MEDIA_SERVER_PASSWORD)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(local_file_path, remote_file_path)
        sftp.close()
        transport.close()
        self.uploaded = True
        self.save()
        self.notify_user()
    
    def save(self, *args, **kwargs):
        if not self.id and self.encode:
            self.encoding = True
        super(MediaBase, self).save(*args, **kwargs)
    
    class Meta:
        ordering = ('-date_added',)
        verbose_name = "Media File"
        verbose_name_plural = "Media Files"
            
    def __unicode__(self):
        return u'%s' % self.title

def check_file_changed(sender, **kwargs):
    instance = kwargs['instance']
    if instance.id and hasattr(instance.file.file, "temporary_file_path"):
        old_instance = sender.objects.get(id=instance.id)
        compare_cmd = 'cmp "%s" "%s"' % (os.path.join(settings.MEDIA_ROOT, old_instance.file.name), os.path.join(settings.MEDIA_ROOT, instance.file.file.temporary_file_path()))
        changed = subprocess.Popen(compare_cmd, stdout=subprocess.PIPE, shell=True).communicate()[0]
        if changed:
            instance.uploaded = False
            instance.encoded = False
            instance.encoding = True
            old_instance.file.delete(save=False)
        
class Video(MediaBase):
    thumbnail_image = FilerImageField(blank=True, null=True, help_text="Set this to upload your own thumbnail image for a video")
    auto_thumbnail = models.BooleanField(default=False, help_text="Will auto generate the thumbnail from the video file if checked")
    thumbnail_offset = models.PositiveIntegerField(blank=True, default=4, help_text="Number of seconds into the video to take the auto thumbnail")
    generated_thumbnail = models.FileField(upload_to=get_media_upload_to, null=True, blank=True, storage=OverwritingStorage())
    objects = MediaManager()
    
    def get_video_url(self):
        return "rtmp://%s/%s/mp4:%s.%s" % (multimedia_settings.MEDIA_SERVER_HOST, multimedia_settings.MEDIA_SERVER_VIDEO_BUCKET, self.id, self.container)
    
    def get_screenshot(self):
        if self.thumbnail_image:
            return self.thumbnail_image
        elif self.auto_thumbnail:
            return self.generated_thumbnail
        return None
    
    def get_profile(self):
        return multimedia_settings.MULTIMEDIA_VIDEO_PROFILES[self.profile]
    
    def get_remote_path(self):
        return os.path.join(settings.MEDIA_SERVER_VIDEO_PATH, "%s.%s" % (self.id, self.container))
    
    def get_thumb_output_path(self):
        return "multimedia/%s/%s/%s.jpg" % (self.file_type,self.slug,self.id)
    
    def admin_thumbnail(self):
        return render_to_string("multimedia/screenshot_admin.html",{"img":self.get_screenshot()})
    admin_thumbnail.allow_tags = True
    admin_thumbnail.short_description = "Thumbnail"
    
    @property
    def thumbnail_cmd(self):
        thumbnail_cmd = self.get_profile().get("thumbnail_cmd")
        input_path = os.path.join(settings.MEDIA_ROOT, self.file.name)
        output_path = os.path.join(settings.MEDIA_ROOT, "multimedia/%s/%s/%s.jpg" % (self.file_type,self.slug,self.id))
        args = {"input":input_path, "offset":str(self.thumbnail_offset), "output":output_path}
        return str(thumbnail_cmd % args)
    
    def make_thumbnail(self):
        command = shlex.split(self.thumbnail_cmd)
        process = subprocess.call(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        f = open(os.path.join(settings.MEDIA_ROOT, self.get_thumb_output_path()))
        self.generated_thumbnail.save("%s.jpg" % (self.id,), SimpleUploadedFile("%s.jpg" % (self.id,), f.read(), content_type="image/jpg"), save=False)
        self.save(make_thumbnail=False)
        f.close()
    
    def save(self, make_thumbnail=True, *args, **kwargs):
        from tasks import encode_media, generate_thumbnail, upload_media
        if not self.id:
            self.file_type = "video"
        super(Video, self).save(*args, **kwargs)
        if self.encode and (not self.encoded):
            #encode then upload
            encode_media.delay(self.id, callback=subtask(upload_media))
        if self.auto_thumbnail and make_thumbnail:
            generate_thumbnail.delay(self.id)
    
    class Meta:
        verbose_name = "Video File"
        verbose_name_plural = "Video Files"
        
pre_save.connect(check_file_changed, sender=Video)
        
class Audio(MediaBase):
    def get_profile(self):
        return multimedia_settings.MULTIMEDIA_AUDIO_PROFILES[self.profile]
    
    def get_remote_path(self):
        return os.path.join(multimedia_settings.MEDIA_SERVER_AUDIO_PATH, "%s.%s" % (self.id, self.container))
    
    def save(self, *args, **kwargs):
        from tasks import encode_media, upload_media
        if not self.id:
            self.file_type = "audio"
        super(Audio, self).save(*args, **kwargs)
        if self.encode and (not self.encoded):
            encode_media.delay(self.id, callback=subtask(upload_media))
        
    class Meta:
        verbose_name = "Audio File"
        verbose_name_plural = "Audio Files"

pre_save.connect(check_file_changed, sender=Audio)

