# -*- coding: utf-8 -*-

import re
import urllib
from celery.task import Task, task
from celery.registry import tasks
from django.conf import settings
import time
from rapidsms_httprouter.models import Message
from ureport.models import SentToMtrac, AutoregGroupRules, MessageDetail, MessageAttribute, Settings
from script.models import Script

import logging

log = logging.getLogger(__name__)


@task
def ping(ignore_result=True):
    log.info("[ping-task] pong.")
    print "pong"
    return "pong"


@task
def start_poll(poll, ignore_result=True):
    log.info("[start-poll-task] Starting poll [" + str(poll.pk) + "] ...")
    if not poll.start_date:
        poll.start()
    log.info("[start-poll-task] Poll start complete.")


@task
def reprocess_responses(poll, ignore_result=True):
    if poll.responses.exists():
        poll.reprocess_responses()


@task
def process_message(pk, ignore_result=True, **kwargs):
    try:
        message = Message.objects.get(pk=pk)
        alert_setting = Settings.objects.get(attribute="alerts")
        if alert_setting.value == "true":
            alert, _ = MessageAttribute.objects.get_or_create(name="alert")
            msg_a = MessageDetail.objects.create(message=message, attribute=alert, value='true')
    except Message.DoesNotExist:
        process_message.retry(args=[pk], countdown=15, kwargs=kwargs)


@task
def reprocess_groups(group, ignore_result=True):
    try:
        scripts = Script.objects.filter(
            pk__in=['ureport_autoreg', 'ureport_autoreg_luo', 'ureport_autoreg2', 'ureport_autoreg_luo2'])
        ar = AutoregGroupRules.objects.get(group=group)
        print 'here'
        if ar.rule_regex:
            regex = re.compile(ar.rule_regex, re.IGNORECASE)
            for script in scripts:
                responses = script.steps.get(order=1).poll.responses.all()
                for response in responses:
                    if regex.search(response.message.text):
                        response.contact.groups.add(group)
            print 'finished'
    except:
        print 'failed'
        pass


@task
def push_to_mtrac(messages):
    messages = list(Message.objects.filter(pk__in=messages))
    for message in messages:
        try:
            message = message.senttomtrac
            log.info("Already Sent message to Mtrac on %s" % message.senttomtrac.sent_on)
            continue
        except SentToMtrac.DoesNotExist:
            pass
        params = urllib.urlencode({'message': message.text, 'sender': message.connection.identity,
                                   'backend': getattr(settings, 'MTRAC_PUSH_BACKEND'),
                                   'password': getattr(settings, 'MTRAC_ROUTER_PASSWORD')})
        try:
            f = None
            # f = urllib.urlopen("%s?%s" % (getattr(settings, 'MTRAC_ROUTER_URL'), params))
            pass
        except Exception, e:
            log.error(str(e))
            continue
        if f.getcode() != 200:
            log.error("Status Mtrac returned (%d):" % f.getcode())
            continue
        SentToMtrac.objects.create(message=message)
    log.info("Pushed messages to Mtrac")


