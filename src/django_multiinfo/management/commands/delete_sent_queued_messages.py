# -*- coding: utf-8 -*-

import logging

from django.core.management.base import BaseCommand

from django_multiinfo.models import SmsMessage, SmsStatus


class Command(BaseCommand):
    help = 'Delete sent queued messages'

    def handle(self, *args, **options):
        sent_qs = SmsMessage.objects.filter(status=SmsStatus.posted).order_by('created')
        if not sent_qs.exists():  # pragma: no cover
            logging.debug('No messages to delete')
            return

        logging.debug(
            "Deleting queued messages, count: %s, first: %s, last: %s", sent_qs.count(),
            sent_qs.first().created.isoformat(), sent_qs.last().created.isoformat()
        )
        sent_qs.delete()
        logging.debug('Queued messages deleted')
