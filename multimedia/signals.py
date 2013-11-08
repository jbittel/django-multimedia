from filecmp import cmp
import os

from django.conf import settings


def set_encode_profiles(sender, instance, **kwargs):
    """
    Signal: pre_save
    Sender: Video, Audio

    Prior to saving, store the currently configured encoding profiles
    so we can later detect if the file needs to be encoded. If a new
    file is being uploaded, force the re-encode.
    """
    # Store the currently configured encoding profiles so we can
    # compare against them later
    if instance.pk:
        instance._profiles = set(list(instance.profiles.values_list('pk', flat=True)))
    else:
        instance._profiles = set(list())

    # If a new file is being uploaded and it's different than the
    # existing file, set it to be encoded
    if hasattr(instance.file.file, 'temporary_file_path'):
        try:
            current = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            pass
        else:
            current_file = os.path.join(settings.MEDIA_ROOT, current.file.name)
            new_file = os.path.join(settings.MEDIA_ROOT,
                                    instance.file.file.temporary_file_path())
            if not cmp(current_file, new_file):
                instance._profiles = set(list())
            current.file.delete(save=False)


def encode_profiles_changed(sender, instance, action, **kwargs):
    """
    Signal: m2m_changed
    Sender: MediaBase.profiles.through

    If the associated encoding profiles change, encode the media
    using all added profiles if it is not currently encoding. Only
    pay attention to the post_add action, as that's when the updated
    relations are available.
    """
    if action in ['post_add']:
        added_profiles = list(kwargs['pk_set'].difference(instance._profiles))
        if added_profiles and not instance.encoding:
            instance.encode(profiles=added_profiles)


def thumbnail_offset_changed(sender, instance, **kwargs):
    """
    Signal: pre_save
    Sender: Video

    If the thumbnail offset has changed, regenerate it with the
    changed offset value.
    """
    from .tasks import generate_thumbnail
    try:
        current = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        pass
    else:
        if current.auto_thumbnail_offset != instance.auto_thumbnail_offset:
            generate_thumbnail.apply_async((instance.model_name, current.pk),
                                           countdown=5)
