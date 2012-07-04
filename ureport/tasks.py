from celery.task import Task, task
from celery.registry import tasks
from rapidsms_httprouter.models import Message

from uganda_common.utils import ExcelResponse
from ureport.models import *
from poll.models import ResponseCategory, Poll, Response
from django.db import transaction
from django.db import IntegrityError
from script.models import Script
from django.contrib.auth.models import  Group



@task
def start_poll(poll):
    if not poll.start_date:
        poll.start()

@task
def reprocess_responses(poll):
    poll.reprocess_responses()

@task
def process_message(pk,**kwargs):

    try:
        message=Message.objects.get(pk=pk)
        alert_setting=Settings.objects.get(attribute="alerts")
        if alert_setting.value=="true":
            alert,_=MessageAttribute.objects.get_or_create(name="alert")
            msg_a=MessageDetail.objects.create(message=message,attribute=alert,value='true')
    except Message.DoesNotExist:
        process_message.retry(args=[pk], countdown=15, kwargs=kwargs)



@task
def reprocess_groups():
    try:
        scripts=Script.objects.filter(pk__in=['ureport_autoreg', 'ureport_autoreg_luo','ureport_autoreg2', 'ureport_autoreg_luo2'])
        word_dict=dict(AutoregGroupRules.objects.exclude(values=None).values_list('group__name','values'))
        for script in scripts:
            responses=script.steps.get(order=1).poll.responses.all()
            for response in responses:
                txt=response.message.text.strip().lower()

                matched=False

                for group_pk, word_list in word_dict.items():
                    for word in word_list.split(","):
                        if word in txt.split():
                            if response.contact and group not in response.contact.groups.all():
                                response.contact.groups.add(Group.objects.get(pk=group_pk))
                                matched=True
                                break
    except:
        pass
