# -*- coding: utf-8 -*-
from django.db import models
from poll.models import Poll, LocationResponseForm,Response, STARTSWITH_PATTERN_TEMPLATE,ResponseCategory
from rapidsms.models import Contact, Connection,Backend
from django.contrib.auth.models import User, Group
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.conf import settings
from rapidsms.contrib.locations.models import Location
from eav.models import Attribute
from django.core.exceptions import ValidationError
from script.signals import *
from script.models import *
from script.utils.handling import find_closest_match, find_best_response
from rapidsms_httprouter.models import Message, MessageBatch
from unregister.models import Blacklist
from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from rapidsms_xforms.models import  XFormField
from ussd.models import ussd_pre_transition,Menu, ussd_complete, Navigation, TransitionException, Field, Question,StubScreen
from celery.contrib import rdb



import datetime
import re
import difflib
import urllib2
from script.signals import script_progress_was_completed


class IgnoredTags(models.Model):
    poll = models.ForeignKey(Poll)
    name = models.CharField(max_length=20)

    def __unicode__(self):
        return '%s' % self.name

class QuoteBox(models.Model):
    question = models.TextField()
    quote = models.TextField()
    quoted = models.TextField()
    creation_date = models.DateTimeField(auto_now=True)

    class Meta:
        get_latest_by = 'creation_date'

class TopResponses(models.Model):
    poll = models.ForeignKey(Poll, related_name="top_responses")
    quote = models.TextField()
    quoted = models.TextField()

class EquatelLocation(models.Model):
    serial=models.CharField(max_length=50)
    segment=models.CharField(max_length=50,null=True)
    location=models.ForeignKey(Location)
    name=models.CharField(max_length=50,null=True)

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


class Ureporter(Contact):
    def age(self):
        if self.birthdate:
            return (datetime.datetime.now() - self.birthdate).days / 365
        else:
            return ""
    def is_active(self):
        return not Blacklist.objects.filter(connection=self.default_connection).exists()

    def join_date(self):
        ss = ScriptSession.objects.filter(connection__contact=self)
        if ss.exists():
            return ScriptSession.objects.filter(connection__contact=self)[0].start_time.date()
        else:
            messages = Message.objects.filter(connection=self.default_connection).order_by('date')
            if messages.exists():
                return messages[0].date
            else:
                return None

    def quit_date(self):
        quit_msg = Message.objects.filter(connection__contact=self,application="unregister")
        if quit_msg.exists():
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

            ]

        proxy = True


def autoreg(**kwargs):
    connection = kwargs['connection']
    progress = kwargs['sender']
    if progress.script.slug in progress.script.slug in ['ureport_autoreg2', 'ureport_autoreg_luo2']:
        connection.contact = Contact.objects.create(name='Anonymous User')
        connection.save()
        session = ScriptSession.objects.filter(script=progress.script, connection=connection).order_by('-end_time')[0]
        script = progress.script
        youthgrouppoll = script.steps.get(order=1).poll
        districtpoll = script.steps.get(order=2).poll
        namepoll = script.steps.get(order=3).poll
        agepoll = script.steps.get(order=4).poll
        genderpoll = script.steps.get(order=5).poll
        villagepoll = script.steps.get(order=6).poll
        contact = connection.contact
        name = find_best_response(session, namepoll)
        if name:
            contact.name = name[:100]

        contact.reporting_location = find_best_response(session, districtpoll)

        age = find_best_response(session, agepoll)
        if age and age < 100:
            contact.birthdate = datetime.datetime.now() - datetime.timedelta(days=(365 * int(age)))

        gresps = session.responses.filter(response__poll=genderpoll, response__has_errors=False).order_by('-response__date')
        if gresps.count():
            gender = gresps[0].response
            if gender.categories.filter(category__name='male').count():
                contact.gender = 'M'
            elif gender.categories.filter(category__name='female').exists():
                contact.gender = 'F'

        village = find_best_response(session, villagepoll)
        if village:
            contact.village = village

        group_to_match = find_best_response(session, youthgrouppoll)
        default_group = None
        if progress.language:
            contact.language = progress.language
        if Group.objects.filter(name='Other uReporters').count():
            default_group = Group.objects.get(name='Other uReporters')
        if group_to_match :
            for g in re.findall(r'\w+', group_to_match):
                if g:
                    group = find_closest_match(str(g), Group.objects.exclude(name__in=["MP","delegate"]))
                    if group:
                        contact.groups.add(group)
                        break

            if default_group:
                contact.groups.add(default_group)
        elif default_group:
            contact.groups.add(default_group)

        if not contact.name:
            contact.name = 'Anonymous User'
        contact.save()

        total_ureporters = Contact.objects.exclude(connection__identity__in=Blacklist.objects.values_list('connection__identity')).count()
        if total_ureporters % getattr(settings, 'USER_MILESTONE', 500) == 0:
            recipients = getattr(settings, 'ADMINS', None)
            if recipients:
                recipients = [email for name, email in recipients]
            mgr = getattr(settings, 'MANAGERS', None)
            if mgr:
                for email in mgr:
                    recipients.append(email)
            send_mail("UReport now %d voices strong!" % total_ureporters, "%s (%s) was the %dth member to finish the sign-up.  Let's welcome them!" % (contact.name, connection.identity, total_ureporters), 'root@uganda.rapidsms.org', recipients, fail_silently=True)



def get_results(poll):
    cats=[]
    response_count=poll.responses.count()
    if poll.categories.all().exists():
        for category in poll.categories.all():
            ccount=poll.responses.filter(categories__category=category).count()
            try:
                ccount_p=int(ccount*100/response_count)
            except ZeroDivisionError:
                return "0 responses"
            cats.append(str(category.name)+":"+str(ccount_p)+"%")
        return " ".join(cats)
    else:
        return str(response_count)+" responses"

def update_poll_results():
    latest_polls=Poll.objects.filter(categories__name__in=['yes','no']).distinct().order_by('-pk')
    res1=Menu.objects.get(slug="res1")

    res1.label=latest_polls[0].name
    res1.save()
    res2=Menu.objects.get(slug="res2")
    res2.label=latest_polls[1].name
    res2.save()
    res3=Menu.objects.get(slug="res3")
    res3.label=latest_polls[2].name
    res3.save()
    res11=Menu.objects.get(slug="res11")
    res11.label=get_results(latest_polls[0])
    res11.save()
    res21=Menu.objects.get(slug="res21")
    res21.label=get_results(latest_polls[1])
    res21.save()

    res31=Menu.objects.get(slug="res31")
    res31.label=get_results(latest_polls[2])
    res31.save()

def check_conn(sender, **kwargs):
    #delete bad connections
    c = kwargs['instance']
    if not c.identity.isdigit():
        c.delete()
        return True
    if c.identity[0:5]=="25671":
        utl=Backend.objects.get(name="utl")
        Connection.objects.filter(pk=c.pk).update(backend=utl)
        return True
def update_latest_poll(sender, **kwargs):

    poll=kwargs['instance']
    if poll.categories.filter(name__in=['yes','no']):
        try:
            xf=XFormField.objects.get(name='latest_poll')
            xf.question=poll.question
            xf.command="poll_"+str(poll.pk)
            xf.save()
            stub_screen=StubScreen.objects.get(slug='question_response')
            if poll.default_response:
                stub_screen.text=poll.default_response
                stub_screen.save()
            else:
                stub_screen.text="Thanks For Your Response."
                stub_screen.save()
            update_poll_results()
        except (XFormField.DoesNotExist,StubScreen.DoesNotExist):         
            pass

        try:
            Menu.tree.rebuild()
        except:
            pass

def ussd_poll(sender, **kwargs):
    connection=sender.connection
    if not  sender.connection.contact:
        connection.contact = Contact.objects.create(name='Anonymous User')

        try:
            serial=sender.navigations.order_by('date')[1].response.rsplit("_")[0]
            connection.contact.reporting_location=EquatelLocation.objects.get(serial=serial).location
            connection.contact.save()
        except EquatelLocation.DoesNotExist:
            pass
        connection.save()
        equatel,created=Group.objects.get_or_create(name="equatel")
        connection.contact.groups.add(equatel)

    if sender.navigations.filter(screen__slug='weekly_poll').exists():
        field=XFormField.objects.get(name="latest_poll")
        nav=sender.navigations.filter(screen__slug='weekly_poll').latest('date')
        poll=Poll.objects.get(pk=int(field.command.rsplit('_')[1]))
        if poll.categories.filter(name__in=["yes","no"]):
            yes=poll.categories.get(name="yes")
            no=poll.categories.get(name='no')
            cats={'1':['yes',yes],'2':['no',no]}
            msg=Message.objects.create(connection=connection,text=cats[nav.response][0],direction="I")
            resp = Response.objects.create(poll=poll, message=msg, contact=connection.contact, date=nav.date)
            resp.categories.add(ResponseCategory.objects.create(response=resp, category=cats[nav.response][1]))
    #update results
    update_poll_results()

    if sender.navigations.filter(screen__slug='send_report'):
        Message.objects.create(connection=connection,text=sender.navigations.filter(screen__slug='send_report').latest('date').response,direction="I")


def add_to_poll(sender,**kwargs):
    try:
        contact=kwargs.get('instance').connection.contact
        poll=Poll.objects.get(name="blacklist")
        poll.contacts.add(contact)
    except:
        pass
    
def normalize_poll_rules(sender,**kwargs):
    pass



script_progress_was_completed.connect(autoreg, weak=False)
post_save.connect(check_conn, sender=Connection, weak=False)
post_save.connect(update_latest_poll, sender=Poll, weak=False)
ussd_complete.connect(ussd_poll, weak=False)
post_save.connect(add_to_poll, sender=Blacklist, weak=False)