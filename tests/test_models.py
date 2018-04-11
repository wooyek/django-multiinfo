#!/usr/bin/env python
# -*- coding: utf-8 -*-
import six
from django.contrib import admin
from django.core.management import execute_from_command_line
from django.test import TestCase, override_settings
from django.utils import timezone
from mock import mock, patch

from django_multiinfo import models
from django_multiinfo.admin import SmsMessageAdmin
from django_multiinfo.factories import SmsMessageFactory
from django_multiinfo.models import SmsMessage, SmsStatus


class SmsMessageModel(TestCase):

    @patch('multiinfo.core.ApiClient.request')
    def test_send(self, request):
        body = "Ojciec Wirgiliusz uczył dzieci swoje. Na głowie przy tym stojąc wiele lat."
        item = models.SmsMessage(to=333, body=body)
        assert not request.called
        item.send()
        assert request.called
        params = request.call_args[1]['params']
        assert 333 == params['dest']
        assert body == params['text']

    @patch("django_multiinfo.models.SmsMessage.send")
    def test_send_queued_limit(self, send):
        SmsMessageFactory.create_batch(5)
        SmsMessage.send_queued(3)
        self.assertEqual(3, send.call_count)

    @patch("django_multiinfo.models.SmsMessage.send")
    def test_send_queued(self, send):
        SmsMessageFactory.create_batch(11, status=SmsStatus.posted)
        SmsMessageFactory.create_batch(5)
        SmsMessage.send_queued()
        self.assertEqual(5, send.call_count)

    def test_str(self):
        o = SmsMessage(body="ążśźćńółĄŻŚŹĘĆŃÓŁ", to="b")
        self.assertEqual(u"SmsMessage:b:ążśźćńółĄŻŚŹĘĆŃÓŁ", six.text_type(o))

    @patch('django_multiinfo.models.SmsMessage.send')
    def test_queue(self, send):
        item = models.SmsMessage.queue(to=1, body='foo')
        self.assertEqual(models.SmsStatus.created, item.status)
        assert not send.called

    @override_settings(SMS_QUEUE_EAGER=True)
    @patch('django_multiinfo.models.SmsMessage.send')
    def test_queue_eager(self, send):
        item = models.SmsMessage.queue(to=1, body='foo')
        self.assertEqual(models.SmsStatus.created, item.status)
        assert send.called


class SmsStatusTests(TestCase):
    def test_values(self):
        self.assertEqual([0, 1, 2], SmsStatus.values())


class CommandTests(TestCase):
    @patch("django_multiinfo.models.SmsMessage.send_queued")
    def test_send_command(self, send_queued):
        execute_from_command_line(argv=["", "send_queued_messages"])
        self.assertTrue(send_queued.called)

    @patch("django_multiinfo.management.commands.delete_sent_queued_messages.logging")
    def test_delete_command(self, mock_logger):
        SmsMessageFactory.create_batch(2, status=SmsStatus.posted)
        SmsMessageFactory.create_batch(2)
        now = timezone.now()
        SmsMessage.objects.update(created=now)
        self.assertEqual(2, SmsMessage.objects.filter(status=SmsStatus.posted).count())

        execute_from_command_line(argv=["", "delete_sent_queued_messages"])
        mock_logger.debug.assert_has_calls([
            mock.call(u"Deleting queued messages, count: %s, first: %s, last: %s", 2, now.isoformat(), now.isoformat()),
            mock.call(u"Queued messages deleted")
        ])
        self.assertEqual(0, SmsMessage.objects.filter(status=SmsStatus.posted).count())


class TestAdmin(TestCase):
    def test_admin(self):
        admin.autodiscover()

    @patch("django_multiinfo.models.SmsMessage.bulk_send")
    def test_send(self, bulk_send):
        qry = SmsMessage.objects.all()
        SmsMessageAdmin(SmsMessage, None).bulk_send(None, qry)
        self.assertTrue(bulk_send.called)

    def test_checks(self):
        from django.core.management import BaseCommand
        BaseCommand().check(display_num_errors=True)


class TestWorker(TestCase):
    def test_worker(self):
        pass
