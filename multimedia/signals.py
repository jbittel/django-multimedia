from filecmp import cmp
import os

from django.conf import settings


def check_file_changed(sender, instance, **kwargs):
    """
    Signal: pre_save
    Sender: MediaBase

    Prior to saving, check to see if the uploaded file is different
    than the existing file. If so, set it to be encoded.
    """
    if instance.id and hasattr(instance.file.file, "temporary_file_path"):
        current = sender.objects.get(pk=instance.id)
        if not cmp(os.path.join(settings.MEDIA_ROOT, current.file.name),
                   os.path.join(settings.MEDIA_ROOT, instance.file.file.temporary_file_path())):
            instance.uploaded = False
            instance.encoded = False
            instance.encoding = True
        current.file.delete(save=False)


def encode_on_change(sender, instance, action, **kwargs):
    """
    Signal: m2m_changed
    Sender: MediaBase.profiles.through

    Whenever the configured encoding profiles are changed, encode
    the media if it has not already been encoded. Only pay attention
    to the post_* actions, as that's when the updated relations will
    be found in the table.
    """
    if action in ['post_add', 'post_remove']:
        if not instance.encoded:
            instance.encode()