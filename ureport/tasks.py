# -*- coding: utf-8 -*-

import re
import urllib
from celery.task import Task, task
from celery.registry import tasks
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Q
from openpyxl import reader
from rapidsms_httprouter.models import Message
from ureport.models import SentToMtrac, AutoregGroupRules, MessageDetail, MessageAttribute, Settings, ExportedPoll, UPoll
from script.models import Script

import logging
from rapidsms.models import Connection, Contact
import utils

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


@task
def process_uploaded_contacts(upload):
    upload.process()
    user = upload.user
    if user.email:
        msg = "Hi %s,\nThe Contacts that you uploaded have been added to Ureport. If there were any unprocessed " \
              "contacts, please find them below" \
              "\n%s" % (user.username, upload.get_unprocessed())
        send_mail('Contacts uploaded', msg, "", [user.email], fail_silently=False)


@task
def process_assign_group(upload, group, user):
    def check_con_or_cont(l):
        for c in l:
            try:
                Connection.objects.get(Q(pk=int(c)) | Q(identity=c))
            except Connection.DoesNotExist:
                return False
            except ValueError:
                continue
        return True

    excel = reader.excel.load_workbook(upload)
    rows = []
    for sheet in excel.worksheets:
        for row in sheet.rows:
            r = []
            for cell in row:
                r.append(cell.value)
            rows.append(tuple(r))
    with_error = []
    con = Connection if check_con_or_cont([r[0] for r in rows]) else Contact
    for row in rows:
        try:
            if hasattr(con, 'identity'):
                c = Connection.objects.get(pk=row[0])
                c.contact.groups.add(group)
            else:
                c = Contact.objects.get(pk=row[0])
                c.groups.add(group)

        except Exception, e:
            with_error.append(("Error:", row, str(e)))
    user = User.objects.get(username=user)
    if user.email:
        msg = "Hi %s,\nThe Contacts that you uploaded have been added to the group. If there were any unprocessed " \
              "contacts, please find them below" \
              "\n%s" % (user.username, str(with_error))
        send_mail('Contacts Added to Group', msg, "", [user.email], fail_silently=False)


@task
def export_poll(poll_id, host, username=None):
    poll = UPoll.objects.get(pk=poll_id)
    ExportedPoll.objects.create(poll=poll)
    utils.export_poll(poll)
    if username:
        user = User.objects.get(username=username)
        if user.email:
            msg = "Hi %s,\nThe poll(%s) has been exported and is now ready for download." \
                  "\nPlease find it here %s\nThank You" % (
                      user.username, poll.name, poll.get_export_path(host))
            send_mail('Contacts Added to Group', msg, "", [user.email], fail_silently=False)