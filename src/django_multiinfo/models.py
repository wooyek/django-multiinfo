import logging
from collections import OrderedDict
from datetime import datetime, timedelta
from enum import IntEnum

import six
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from multiinfo import core
from multiinfo.endpoints import STATUS_MAPPING

log = logging.getLogger(__name__)


class ChoicesIntEnum(IntEnum):
    """Extends IntEum with django choices generation capability"""

    @classmethod
    def choices(cls):
        return [(item.value, _(item.name.replace("_", " ").capitalize())) for item in cls]

    @classmethod
    def values(cls):
        return [item.value for item in cls]


class SmsStatus(ChoicesIntEnum):
    created = 0
    posted = 1
    busy = 2
    error = 3
    discarded = 4


@six.python_2_unicode_compatible
class SmsMessage(models.Model):
    status = models.PositiveSmallIntegerField(choices=SmsStatus.choices(), default=SmsStatus.created)
    created = models.DateTimeField(auto_now_add=True)
    ts = models.DateTimeField(blank=True, null=True, auto_now=True)
    to = models.CharField(max_length=15, blank=True, null=True)
    body = models.TextField()
    eid = models.BigIntegerField(null=True, blank=True)
    key = models.CharField(max_length=150, null=True, blank=True)

    class Meta:
        index_together = ('to', 'key')

    def __str__(self):
        return u"{}:{}:{}".format(self.__class__.__name__, self.to, self.body)

    @classmethod
    def queue(cls, **kwargs):
        item = cls.objects.create(**kwargs)
        if settings.SMS_QUEUE_EAGER:
            item.send()
        return item

    def _send(self):
        data = {
            "dest": self.to,
            "text": self.body,
        }
        now = datetime.utcnow().replace(tzinfo=timezone.get_default_timezone())
        self.ts = now
        self.status = SmsStatus.busy
        self.save()
        sms = core.multiinfo_api.send_long_sms.send(**data)
        self.eid = sms.message_id
        self.status = SmsStatus.posted
        self.save()

    @classmethod
    def send_queued(cls, limit=None):
        seconds = settings.SMS_QUEUE_RETRY_SECONDS
        retry = timezone.now() - timedelta(seconds=seconds)
        qry = cls.objects.filter(Q(status=SmsStatus.created) | Q(status=SmsStatus.busy, ts__lte=retry)).order_by("created")
        if limit:
            qry = qry[:limit]
        cls.bulk_send(qry)
        return qry.first() is not None

    def send(self, fail_silently=True):
        if self.created:
            age_hours = (timezone.now() - self.created).total_seconds() / 3600
            if settings.SMS_QUEUE_DISCARD_HOURS and age_hours > settings.SMS_QUEUE_DISCARD_HOURS:
                self.status = SmsStatus.discarded
                self.save()
                return
        try:
            self._send()
        except Exception as ex:
            if fail_silently is False:
                raise ex
            # Log error but do not block other messages
            logging.error("SMS send failed", exc_info=ex)

    @classmethod
    def bulk_send(cls, qry):
        for message in qry:
            message.send()

    def get_message_info(self):
        assert self.eid, "Cannot get info for message {}, no eid to use with multiinfo.".format(self.pk)
        data = core.multiinfo_api.info_sms.get(self.eid)
        return SmsMessageInfo.create_from_data(data, self)


STATUS_CHOICES = OrderedDict(sorted(STATUS_MAPPING.items(), key=lambda x: x[0])).items()


@six.python_2_unicode_compatible
class SmsMessageInfo(models.Model):
    sms_message = models.ForeignKey(SmsMessage, null=True, blank=True, on_delete=models.CASCADE)
    send_error = models.TextField(null=True, blank=True)
    ts = models.DateTimeField(auto_now=True)

    dest = models.CharField(max_length=15)
    body_type = models.PositiveSmallIntegerField()
    encoding = models.PositiveSmallIntegerField()
    connector_id = models.BigIntegerField()
    sms_id = models.BigIntegerField()
    last_change_date = models.DateTimeField()
    message_status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES)
    priority = models.PositiveSmallIntegerField()
    protocol = models.PositiveSmallIntegerField()
    report_delivery = models.BooleanField()
    request_status = models.IntegerField()
    service_id = models.IntegerField()
    response_to_id = models.BigIntegerField()
    send_date = models.DateTimeField()
    valid_to = models.DateTimeField()
    sender_name = models.CharField(max_length=150)
    text = models.TextField()

    @classmethod
    def create_from_data(cls, data, sms_message=None):
        data['message_status'] = data.pop('message_status')[0]
        return SmsMessageInfo.objects.create(sms_message=sms_message, **data)
