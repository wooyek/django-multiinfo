#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

import six
from django.conf import settings
from django.contrib import admin
from django.contrib.messages.storage.base import BaseStorage
from django.core.management import execute_from_command_line
from django.test import RequestFactory, TestCase, override_settings
from django.utils import timezone
from mock import mock, patch
from multiinfo.endpoints import parse_status_info

from django_multiinfo import factories, models
from django_multiinfo.admin import SmsMessageAdmin
from django_multiinfo.factories import SmsMessageFactory
from django_multiinfo.models import SmsMessage, SmsStatus


class SmsMessageModelTests(TestCase):

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

    @override_settings(SMS_QUEUE_DISCARD_HOURS=2)
    @patch('django_multiinfo.models.SmsMessage._send')
    def test_discard_message(self, send):
        send.side_effect = Exception("Foo")
        item = models.SmsMessage(created=timezone.now() - timedelta(hours=2, seconds=1))
        item.send()
        self.assertEqual(item.status, models.SmsStatus.discarded)
        self.assertFalse(send.called)

    @override_settings(SMS_QUEUE_DISCARD_HOURS=2)
    @patch('django_multiinfo.models.SmsMessage._send')
    def test_discard_message2(self, send):
        send.side_effect = Exception("Foo")
        item = models.SmsMessage(created=timezone.now() - timedelta(days=30, hours=1, seconds=1))
        item.send()
        self.assertEqual(item.status, models.SmsStatus.discarded)

    @override_settings(SMS_QUEUE_DISCARD_HOURS=1)
    @patch('django_multiinfo.models.SmsMessage._send')
    def test_dont_discard_message(self, send):
        send.side_effect = Exception("Foo")
        item = models.SmsMessage(created=timezone.now() - timedelta(seconds=3599))
        item.send()
        self.assertEqual(models.SmsStatus.created, item.status)

    @override_settings(SMS_QUEUE_DISCARD_HOURS=None)
    @patch('django_multiinfo.models.SmsMessage._send')
    def test_dont_discard_message2(self, send):
        send.side_effect = Exception("Foo")
        item = models.SmsMessage(created=timezone.now() - timedelta(seconds=3599))
        item.send()
        self.assertEqual(models.SmsStatus.created, item.status)

    @patch('django_multiinfo.models.SmsMessage._send')
    def test_fail_silently(self, send):
        send.side_effect = Exception("Foo")
        item = models.SmsMessage(created=timezone.now())
        item.send()

    @patch('django_multiinfo.models.SmsMessage._send')
    def test_dont_fail_silently(self, send):
        send.side_effect = Exception("Foo")
        item = models.SmsMessage()
        self.assertRaises(Exception, item.send, fail_silently=False)

    @override_settings(SMS_QUEUE_RETRY_SECONDS=600)
    @patch('django_multiinfo.models.SmsMessage._send')
    def test_retry_busy(self, send):
        seconds = settings.SMS_QUEUE_RETRY_SECONDS + 2
        retry = datetime.now() - timedelta(seconds=seconds)
        message = factories.SmsMessageFactory(
            ts=retry,
            status=SmsStatus.busy,
        )
        models.SmsMessage.objects.all().update(ts=retry)
        message.send_queued()
        self.assertTrue(send.called)

    @override_settings(SMS_QUEUE_RETRY_SECONDS=600)
    @patch('django_multiinfo.models.SmsMessage._send')
    def test_retry_wait(self, send):
        seconds = settings.SMS_QUEUE_RETRY_SECONDS - 2
        retry = datetime.now() - timedelta(seconds=seconds)
        message = factories.SmsMessageFactory(
            ts=retry,
            status=SmsStatus.busy,
        )
        models.SmsMessage.objects.all().update(ts=retry)
        message.send_queued()
        self.assertFalse(send.called)

    @patch('multiinfo.core.multiinfo_api.info_sms.get')
    def test_get_message_info(self, get):
        get.return_value = {
            'request_status': '0',
            'protocol': 0,
            'report_delivery': False,
            'text': 'foobar%0a',
            'body_type': 1,
            'encoding': 0,
            'send_date': datetime(2018, 4, 27, 7, 49, 6),
            'connector_id': 662000123,
            'priority': 0,
            'valid_to': datetime(2018, 4, 30, 7, 49, 6),
            'sms_id': '2322549673',
            'last_change_date': datetime(2018, 2, 27, 7, 58, 6),
            'response_to_id': -1,
            'message_status': (21, 'Wiadomość przesłana pomyślnie'),
            'sender_name': 'FABRIKAM',
            'service_id': 3290,
            'dest': '48197927123'
        }
        item = factories.SmsMessageFactory(eid=123)
        info = item.get_message_info()
        self.assertIsNotNone(info)


class SmsStatusTests(TestCase):
    def test_values(self):
        self.assertEqual([0, 1, 2, 3, 4], SmsStatus.values())


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

    @patch("django_multiinfo.models.SmsMessage.get_message_info")
    def test_get_message_info(self, get_message_info):
        factories.SmsMessageFactory(eid=1)
        qry = SmsMessage.objects.all()
        SmsMessageAdmin(SmsMessage, None).get_message_info(None, qry)
        self.assertTrue(get_message_info.called)

    @patch("django_multiinfo.models.SmsMessage.get_message_info")
    def test_get_not_message_info(self, get_message_info):
        factories.SmsMessageFactory(eid=None)
        qry = SmsMessage.objects.all()
        request = RequestFactory()
        request._messages = BaseStorage(request)
        SmsMessageAdmin(SmsMessage, None).get_message_info(request, qry)
        self.assertFalse(get_message_info.called)


class TestWorker(TestCase):
    def test_worker(self):
        pass


TEST_INFO_2 = """0
2322590614
1
foobar
0
0
3290
662000123
-1
0
270418092727
300418092728
False
CONTOSO
48121662123
7
2018-02-27 08:17:28"""


# noinspection PyMethodMayBeStatic
class SmsMessageInfoTests(TestCase):
    def test_create(self):
        data = parse_status_info(TEST_INFO_2)
        models.SmsMessageInfo.create_from_data(data)
