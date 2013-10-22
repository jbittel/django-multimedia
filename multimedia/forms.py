from django import forms
from models import Video, Audio


class VideoAdminForm(forms.ModelForm):
    class Meta:
        model = Video


class AudioAdminForm(forms.ModelForm):
    class Meta:
        model = Audio
