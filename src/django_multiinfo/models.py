import logging
from datetime import datetime
from enum import IntEnum

import six
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

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


@six.python_2_unicode_compatible
class SmsMessage(models.Model):
    status = models.PositiveSmallIntegerField(choices=SmsStatus.choices(), default=SmsStatus.created)
    created = models.DateTimeField(auto_now_add=True)
    ts = models.DateTimeField(blank=True, null=True)
    to = models.CharField(max_length=15, blank=True, null=True)
    body = models.TextField()

    def __str__(self):
        return u"{}:{}:{}".format(self.__class__.__name__, self.to, self.body)

    @classmethod
    def queue(cls, **kwargs):
        item = cls.objects.create(**kwargs)
        if settings.SMS_QUEUE_EAGER:
            item.send()
        return item

    def send(self):
        data = {
            "dest": self.to,
            "text": self.body,
        }
        now = datetime.utcnow().replace(tzinfo=timezone.get_default_timezone())
        self.ts = now
        self.status = SmsStatus.busy
        self.save()
        from multiinfo import core
        core.multiinfo_api.send_long_sms.send(**data)
        self.status = SmsStatus.posted
        self.save()

    @classmethod
    def send_queued(cls, limit=None):
        qry = cls.objects.filter(status=SmsStatus.created).order_by("created")
        if limit:
            qry = qry[:limit]
        cls.bulk_send(qry)
        return qry.first() is not None

    @classmethod
    def bulk_send(cls, qry):
        for message in qry:
            try:
                message.send()
            except Exception as ex:
                # Log error but do not block other messages
                logging.error("SMS send failed", exc_info=ex)
