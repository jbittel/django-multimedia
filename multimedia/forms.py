from django import forms
from models import Video, Audio, VIDEO_PROFILES, AUDIO_PROFILES

class VideoAdminForm(forms.ModelForm):
    profile = forms.ChoiceField(choices=VIDEO_PROFILES)
    
    class Meta:
        model = Video
        
class AudioAdminForm(forms.ModelForm):
    profile = forms.ChoiceField(choices=AUDIO_PROFILES)

    class Meta:
        model = Audio