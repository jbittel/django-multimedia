from django.contrib import admin
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy

from .models import Media
from .models import EncodeProfile


class MediaAdmin(admin.ModelAdmin):
    actions = ['encode']
    list_display = ('title', 'active', 'created', 'modified')
    ordering = ('-created',)

    class Meta:
        model = Media

    def save_model(self, request, obj, form, change):
        if not change:
            obj.owner = request.user
        obj.save()

    def encode(self, request, queryset):
        for media in queryset:
            media.encode()
        meta = self.model._meta
        if len(queryset) == 1:
            message_bit = "%s is" % force_text(meta.verbose_name)
        else:
            message_bit = "%s are" % force_text(meta.verbose_name_plural)
        self.message_user(request, _("Your %s being encoded.") % message_bit)
    encode.short_description = ugettext_lazy("Encode selected %(verbose_name_plural)s")


class EncodeProfileAdmin(admin.ModelAdmin):
    class Meta:
        model = EncodeProfile

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['container']
        else:
            return []


admin.site.register(Media, MediaAdmin)
admin.site.register(EncodeProfile, EncodeProfileAdmin)
