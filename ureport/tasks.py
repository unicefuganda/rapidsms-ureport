from celery.task import Task, task
from celery.registry import tasks
from rapidsms_httprouter.models import Message
from celery.task import PeriodicTask
import os
from django.utils.datastructures import SortedDict
from uganda_common.utils import ExcelResponse
from .models import *
import logging
from celery.contrib import rdb
from xlrd import open_workbook
from .utils import *
import datetime
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from poll.models import ResponseCategory, Poll, Response




@task
def start_poll(poll):
    if not poll.start_date:
        poll.start()

def reprocess_responses(poll):
    poll.reprocess_responses()




