from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from . import models


@admin.register(models.SmsMessage)
class SmsMessageAdmin(admin.ModelAdmin):
    list_display = (
        'created',
        'posted',
        'to',
        'body',
    )
    list_filter = ('status',)
    date_hierarchy = 'created'
    actions = ['bulk_send']
    search_fields = ('to', 'body',)

    # noinspection PyUnusedLocal
    def bulk_send(self, request, queryset):
        models.SmsMessage.bulk_send(queryset)

    bulk_send.short_description = _("bulk send")
