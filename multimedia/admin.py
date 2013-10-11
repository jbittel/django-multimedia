from django.contrib import admin, messages
from models import Video, Audio
from forms import VideoAdminForm, AudioAdminForm


class MediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'profile', 'encoding', 'encoded', 'uploaded', 'date_added', 'date_modified')
    list_display_links = ('id', 'title',)
    prepopulated_fields = {'slug': ('title',)}
    exclude = ('user', 'file_type',)
    readonly_fields = ('encoded', 'uploaded',)
    list_filter = ('encoded', 'uploaded', 'encoding',)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
        obj.save()
        if not obj.encoded:
            messages.success(request, "Your file is being encoded and uploaded.  An email notification will be sent when complete.")

    def encode_again(self, request, queryset):
        for media in queryset:
            media.encoded = False
            media.uploaded = False
            media.encoding = True
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
    readonly_fields = ('encoded', 'uploaded', 'generated_thumbnail',)
    list_display = ('id', 'title', 'profile', 'encoding', 'encoded', 'uploaded', 'date_added', 'date_modified', 'admin_thumbnail',)

    class Meta:
        model = Video


class AudioAdmin(MediaAdmin):
    form = AudioAdminForm

    class Meta:
        model = Audio

admin.site.register(Video, VideoAdmin)
admin.site.register(Audio, AudioAdmin)
