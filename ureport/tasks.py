from celery.task import Task, task
from celery.registry import tasks
from rapidsms_httprouter.models import Message

from uganda_common.utils import ExcelResponse
from ureport.models import *
from poll.models import ResponseCategory, Poll, Response
from django.db import transaction
from django.db import IntegrityError



@task
def start_poll(poll):
    if not poll.start_date:
        poll.start()

@task
def reprocess_responses(poll):
    poll.reprocess_responses()

@task
def process_message(message,**kwargs):
    if hasattr(message, 'db_message'):
        message = message.db_message
    try:

        alert_setting=Settings.objects.get(attribute="alerts")
        if alert_setting.value=="true":
            alert,_=MessageAttribute.objects.get_or_create(name="alert")
            msg_a=MessageDetail.objects.create(message=message,attribute=alert,value='true')
    except IntegrityError,e:
        transaction.rollback()
        process_message.retry(args=[message], exc=e, countdown=30, kwargs=kwargs)




