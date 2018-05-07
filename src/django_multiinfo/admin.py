from django.contrib import admin, messages
from django.utils.translation import ugettext_lazy as _

from . import models


@admin.register(models.SmsMessage)
class SmsMessageAdmin(admin.ModelAdmin):
    list_display = (
        'created',
        'ts',
        'status',
        'to',
        'body',
        'eid',
    )
    list_filter = ('status',)
    date_hierarchy = 'created'
    actions = ['bulk_send', 'get_message_info']
    search_fields = ('to', 'body', 'eid')
    readonly_fields = ('created', 'ts')

    # noinspection PyUnusedLocal
    def bulk_send(self, request, queryset):
        models.SmsMessage.bulk_send(queryset)

    bulk_send.short_description = _("Bulk send")

    # noinspection PyUnusedLocal
    def get_message_info(self, request, queryset):
        if queryset.filter(eid__isnull=True).exists():
            messages.error(request, "Cannot get info if eid is not set. Did those messages have bee send?")
            return
        for item in queryset:
            item.get_message_info()

    get_message_info.short_description = _("Get status information")


@admin.register(models.SmsMessageInfo)
class SmsMessageInfoAdmin(admin.ModelAdmin):
    list_display = (
        'ts',
        'message_status',
        'last_change_date',
        'dest',
        'text',
    )
    list_filter = ('message_status',)
    date_hierarchy = 'ts'
    search_fields = ('dest', 'text', 'sms_id')
