from django.contrib import admin

from .models import Audio
from .models import Video
from .models import EncodeProfile


class MediaAdmin(admin.ModelAdmin):
    actions = ['re_encode']
    list_display = ('title', 'encoding', 'encoded', 'uploaded', 'created', 'modified')
    list_filter = ('encoded', 'uploaded', 'encoding')
    prepopulated_fields = {'slug': ('title',)}

    def save_model(self, request, obj, form, change):
        if not change:
            obj.owner = request.user
        obj.save()
        if not obj.encoded:
            self.message_user(request, "Your file is being encoded. An email notification will be sent when complete.")

    def re_encode(self, request, queryset):
        for media in queryset:
            media.encoded = False
            media.save()
            media.encode()
        if len(queryset) == 1:
            message_bit = "file is"
        else:
            message_bit = "files are"
        self.message_user(request, "Your %s being encoded. An email notification will be sent when complete." % message_bit)
    re_encode.short_description = "Re-encode selected %(verbose_name_plural)s"


class VideoAdmin(MediaAdmin):
    list_display = ('title', 'encoding', 'encoded', 'uploaded', 'created', 'modified', 'thumbnail_html',)

    class Meta:
        model = Video


class AudioAdmin(MediaAdmin):
    class Meta:
        model = Audio


class EncodeProfileAdmin(admin.ModelAdmin):
    class Meta:
        model = EncodeProfile


admin.site.register(Video, VideoAdmin)
admin.site.register(Audio, AudioAdmin)
admin.site.register(EncodeProfile, EncodeProfileAdmin)
