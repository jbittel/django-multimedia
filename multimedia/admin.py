from django.contrib import admin
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy

from .models import Audio
from .models import Video
from .models import EncodeProfile


class MediaAdmin(admin.ModelAdmin):
    actions = ['re_encode']
    list_display = ('title', 'encoding', 'encoded', 'created', 'modified')
    list_filter = ('encoded', 'encoding')
    prepopulated_fields = {'slug': ('title',)}

    def save_model(self, request, obj, form, change):
        if not change:
            obj.owner = request.user
        obj.save()
        meta = self.model._meta
        if not obj.encoded:
            self.message_user(request, _("Your %s is being encoded. An email notification will be sent when complete.") % force_text(meta.verbose_name))

    def re_encode(self, request, queryset):
        for media in queryset:
            media.encoded = False
            media.save()
            media.encode()
        meta = self.model._meta
        if len(queryset) == 1:
            message_bit = "%s is" % force_text(meta.verbose_name)
        else:
            message_bit = "%s are" % force_text(meta.verbose_name_plural)
        self.message_user(request, _("Your %s being encoded. An email notification will be sent when complete.") % message_bit)
    re_encode.short_description = ugettext_lazy("Re-encode selected %(verbose_name_plural)s")


class VideoAdmin(MediaAdmin):
    list_display = ('title', 'encoding', 'encoded', 'created', 'modified', 'thumbnail_html',)

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
