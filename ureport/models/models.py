# -*- coding: utf-8 -*-
from django.db import models
from poll.models import Poll
from rapidsms.models import Contact, Connection
from django.contrib.auth.models import User, Group
from rapidsms.contrib.locations.models import Location
from script.models import ScriptSession
from rapidsms_httprouter.models import Message
from unregister.models import Blacklist
from django.db.models.signals import post_save
from ussd.models import  ussd_complete
import datetime
import re
from script.signals import script_progress_was_completed


class IgnoredTags(models.Model):
    poll = models.ForeignKey(Poll)
    name = models.CharField(max_length=20)

    def __unicode__(self):
        return '%s' % self.name
    class Meta:
        app_label = 'ureport'

class QuoteBox(models.Model):
    question = models.TextField()
    quote = models.TextField()
    quoted = models.TextField()
    creation_date = models.DateTimeField(auto_now=True)

    class Meta:
        get_latest_by = 'creation_date'
        app_label = 'ureport'

class TopResponses(models.Model):
    poll = models.ForeignKey(Poll, related_name="top_responses")
    quote = models.TextField()
    quoted = models.TextField()

    class Meta:
        app_label = 'ureport'

class EquatelLocation(models.Model):
    serial=models.CharField(max_length=50)
    segment=models.CharField(max_length=50,null=True)
    location=models.ForeignKey(Location)
    name=models.CharField(max_length=50,null=True)

    class Meta:
        app_label = 'ureport'

class Permit(models.Model):
    user = models.ForeignKey(User)
    allowed=models.CharField(max_length=200)
    date=models.DateField(auto_now=True)
    def get_patterns(self):
        pats=[]
        ropes=self.allowed.split(",")
        for rop in ropes:
            pattern=re.compile(rop+r"(.*)")
            pats.append(pattern)
        return pats
    def __unicode__(self):
        return self.user.username

    class Meta:
        app_label = 'ureport'


class Ureporter(Contact):
    from_cache = False
    def age(self):
        if self.birthdate:
            return (datetime.datetime.now() - self.birthdate).days / 365
        else:
            return ""
    def is_active(self):
        return not Blacklist.objects.filter(connection=self.default_connection)

    def join_date(self):
        ss = ScriptSession.objects.filter(connection__contact=self)
        if ss:
            return ScriptSession.objects.filter(connection__contact=self)[0].start_time.date()
        else:
            messages = Message.objects.filter(connection=self.default_connection).order_by('date')
            if messages:
                return messages[0].date
            else:
                return None

    def quit_date(self):
        quit_msg = Message.objects.filter(connection__contact=self,application="unregister")
        if quit_msg:
            return quit_msg.latest('date').date
    def messages_count(self):
        return Message.objects.filter(connection__contact=self,direction="I").count()

    class Meta:
        permissions = [
                ("view_numbers", "can view private info"),
                ("restricted_access", "can view only particular pages"),
                ("can_filter", "can view filters"),
                ("can_action", "can view actions"),
                ("view_number", "can view numbers"),
                ("can_export", "can view exports"),
                ("can_forward", "can forward messages"),

            ]

        proxy = True
        app_label = 'ureport'


class MessageAttribute(models.Model):
    '''
    The 'MessageAttribute' model represents a class of feature found
    across a set of messages. It does not store any data values
    related to the attribute, but only describes what kind of a
    message feature we are trying to capture.

    Possible attributes include things like number of replies,severity,department    etc
    '''
    name = models.CharField(max_length=300,db_index=True)
    description = models.TextField(blank=True,null=True)

    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        app_label = 'ureport'

class MessageDetail(models.Model):
    '''
    The 'MessageDetail' model represents information unique to a
    specific message. This is a generic design that can be used to
    extend the information contained in the 'Message' model with
    specific, extra details.
    '''

    message = models.ForeignKey(Message, related_name='details')
    attribute = models.ForeignKey('MessageAttribute')
    value = models.CharField(max_length=500)
    description = models.TextField(null=True)

    def __unicode__(self):
        return u'%s: %s' % (self.message, self.attribute)

    class Meta:
        app_label = 'ureport'

class Settings(models.Model):
    """
    configurable  sitewide settings. Its better to store in db table

    """
    attribute=models.CharField(max_length=50,null=False)
    value=models.CharField(default='',max_length=50,null=True)
    description= models.TextField(null=True)
    user=models.ForeignKey(User,null=True,blank=True)


    class Meta:
        app_label = 'ureport'


class AutoregGroupRules(models.Model):
    group=models.ForeignKey(Group)
    values=models.TextField(default=None)
    class Meta:
        app_label = 'ureport'






from .litseners import  autoreg,check_conn,update_latest_poll,ussd_poll,add_to_poll

script_progress_was_completed.connect(autoreg, weak=False)
post_save.connect(check_conn, sender=Connection, weak=False)
post_save.connect(update_latest_poll, sender=Poll, weak=False)
ussd_complete.connect(ussd_poll, weak=False)
#post_save.connect(add_to_poll, sender=Blacklist, weak=False)