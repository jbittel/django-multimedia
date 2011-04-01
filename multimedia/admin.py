from django.contrib import admin, messages
from models import Video, Audio
from forms import VideoAdminForm, AudioAdminForm

from celery.task.sets import subtask
from tasks import encode_media, generate_thumbnail, upload_media

class MediaAdmin(admin.ModelAdmin):
    list_display = ('id','title','profile','encoding','encoded','uploaded','date_added','date_modified')
    list_display_links = ('id','title',)
    prepopulated_fields = {'slug': ('title',)}
    exclude = ('user','file_type',)
    readonly_fields = ('encoded','uploaded',)
    list_filter = ('encoded','uploaded','encoding',)
    
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()
        if obj.encode and (not obj.encoded):
            messages.success(request, "Your file is being encoded and uploaded.  An email notification will be sent when complete.")
            
    def encode_again(self, request, queryset):
        rows_updated = 0
        for media in queryset:
            if media.encode:
                rows_updated += 1
                encode_media.delay(media.id, callback=subtask(upload_media))
                media.encoded = False
                media.uploaded = False
                media.encoding = True
                media.save()
        if rows_updated == 1:
            message_bit = "Your file is"
        elif rows_updated > 1:
            message_bit = "Your files are"
            
        if rows_updated > 0:
            messages.success(request, "%s being encoded and uploaded.  An email notification will be sent when complete." % message_bit)
        
    encode_again.short_description = "Re-encode and upload media"
    actions = [encode_again,]
                     
class VideoAdmin(MediaAdmin):
    form = VideoAdminForm
    readonly_fields = ('encoded','uploaded','generated_thumbnail',)
    list_display = ('id','title','profile','encoding','encoded','uploaded','date_added','date_modified','admin_thumbnail',)
    
    class Meta:
        model = Video

class AudioAdmin(MediaAdmin):
    form = AudioAdminForm
    
    class Meta:
        model = Audio
        
admin.site.register(Video, VideoAdmin)
admin.site.register(Audio, AudioAdmin)

