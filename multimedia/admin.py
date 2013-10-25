from django.contrib import admin, messages
from forms import VideoAdminForm, AudioAdminForm

from .models import Audio
from .models import Video
from .models import EncodeProfile


class MediaAdmin(admin.ModelAdmin):
    list_display = ('title', 'encoding', 'encoded', 'uploaded', 'created', 'modified')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('encoded', 'uploaded', 'encoding',)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.owner = request.user
        obj.save()
        if not obj.encoded:
            messages.success(request, "Your file is being encoded and uploaded.  An email notification will be sent when complete.")

    def encode_again(self, request, queryset):
        for media in queryset:
            media.encoded = False
            media.save()
        if len(queryset) == 1:
            message_bit = "Your file is"
        else:
            message_bit = "Your files are"

        messages.success(request, "%s being encoded and uploaded.  An email notification will be sent when complete." % message_bit)

    encode_again.short_description = "Re-encode and upload media"
    actions = [encode_again]


class VideoAdmin(MediaAdmin):
    form = VideoAdminForm
    list_display = ('title', 'encoding', 'encoded', 'uploaded', 'created', 'modified', 'thumbnail_html',)

    class Meta:
        model = Video


class AudioAdmin(MediaAdmin):
    form = AudioAdminForm

    class Meta:
        model = Audio


class EncodeProfileAdmin(admin.ModelAdmin):
    class Meta:
        model = EncodeProfile

admin.site.register(Video, VideoAdmin)
admin.site.register(Audio, AudioAdmin)
admin.site.register(EncodeProfile, EncodeProfileAdmin)
