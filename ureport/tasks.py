from celery.task import Task, task
from celery.registry import tasks
from rapidsms_httprouter.models import Message
from ureport.models import *
from script.models import Script

@task
def ping(ignore_result=True):
    print "pong"

@task
def start_poll(poll,ignore_result=True):
    print "[current-flow] Starting poll [" + str(poll.pk) + "] ..."
    if not poll.start_date:
        poll.start()
    print "[current-flow] Poll start complete."

@task
def reprocess_responses(poll,ignore_result=True):
    if poll.responses.exists():
        poll.reprocess_responses()

@task
def process_message(pk,ignore_result=True,**kwargs):

    try:
        message=Message.objects.get(pk=pk)
        alert_setting=Settings.objects.get(attribute="alerts")
        if alert_setting.value=="true":
            alert,_=MessageAttribute.objects.get_or_create(name="alert")
            msg_a=MessageDetail.objects.create(message=message,attribute=alert,value='true')
    except Message.DoesNotExist:
        process_message.retry(args=[pk], countdown=15, kwargs=kwargs)



@task
def reprocess_groups(group, ignore_result=True):
    try:
        scripts=Script.objects.filter(pk__in=['ureport_autoreg', 'ureport_autoreg_luo','ureport_autoreg2', 'ureport_autoreg_luo2'])
        ar=AutoregGroupRules.objects.get(group=group)
        print 'here'
        if ar.rule_regex:
            regex = re.compile(ar.rule_regex, re.IGNORECASE)
            for script in scripts:
                responses=script.steps.get(order=1).poll.responses.all()
                for response in responses:
                    if regex.search(response.message.text):
                        response.contact.groups.add(group)
            print 'finished'
    except:
        print 'failed'
        pass





