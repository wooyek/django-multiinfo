# coding=utf-8

#: Don't queue messages store them and send them immediately
#: Set this to True if you are going to use
SMS_QUEUE_EAGER = False

#: Worker sleep time between queue checkup
SMS_QUEUE_SLEEP_TIME = 15

#: Discard messages after failing delivery for X hours
SMS_QUEUE_DISCARD_HOURS = None

#: Retry stalled messages (status==busy) after X seconds
SMS_QUEUE_RETRY_SECONDS = 300
