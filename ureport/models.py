# -*- coding: utf-8 -*-
from django.db import models
from poll.models import Poll, LocationResponseForm, STARTSWITH_PATTERN_TEMPLATE
from rapidsms.models import Contact, Connection
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
from rapidsms_httprouter.managers import BulkInsertManager
from rapidsms_httprouter.models import Message

import datetime
import re
import difflib

c_bulk_mgr = BulkInsertManager()
c_bulk_mgr.contribute_to_class(Contact, 'bulk')

cn_bulk_mgr = BulkInsertManager()
cn_bulk_mgr.contribute_to_class(Connection, 'bulk')

class IgnoredTags(models.Model):
    poll = models.ForeignKey(Poll)
    name = models.CharField(max_length=20)

    def __unicode__(self):
        return '%s' % self.name

class MassText(models.Model):
    sites = models.ManyToManyField(Site)
    contacts = models.ManyToManyField(Contact, related_name='masstexts')
    user = models.ForeignKey(User)
    date = models.DateTimeField(auto_now_add=True, null=True)
    text = models.TextField()
    objects = (CurrentSiteManager('sites') if getattr(settings, 'SITE_ID', False) else models.Manager())
    bulk = BulkInsertManager()

    class Meta:
        permissions = (
            ("can_message", "Can send messages, create polls, etc"),
        )

class Flag(models.Model):
    """
    a Message flag
    """
    name=models.CharField(max_length=50,unique=True)

    def get_messages(self):
        message_flags=self.messages.values_list('message',flat=True)
        return Message.objects.filter(pk__in=message_flags)

    def __unicode__(self):
        return self.name
    
class MessageFlag(models.Model):
    """ relation between flag and message
    """
    message = models.ForeignKey(Message, related_name='flags')
    flag=models.ForeignKey(Flag,related_name="messages",null=True)

    
def parse_district_value(value):
    location_template = STARTSWITH_PATTERN_TEMPLATE % '[a-zA-Z]*'
    regex = re.compile(location_template)
    toret = find_closest_match(value, Location.objects.filter(type__name='district'))
    if not toret:
        raise ValidationError("We didn't recognize your district.  Please carefully type the name of your district and re-send.")
    else:
        return toret

Poll.register_poll_type('district', 'District Response', parse_district_value, db_type=Attribute.TYPE_OBJECT, \
                        view_template='polls/response_location_view.html',
                        edit_template='polls/response_location_edit.html',
                        report_columns=(('Text', 'text'), ('Location', 'location'), ('Categories', 'categories')),
                        edit_form=LocationResponseForm)


def autoreg(**kwargs):
    connection = kwargs['connection']
    connection.contact = Contact.objects.create(name='Anonymous User')
    connection.save()
    progress = kwargs['sender']
    if not progress.script.slug == 'ureport_autoreg':
        return
    session = ScriptSession.objects.filter(script=progress.script, connection=connection).order_by('-end_time')[0]
    script = progress.script
    youthgrouppoll = script.steps.get(order=1).poll
    districtpoll = script.steps.get(order=3).poll
    namepoll = script.steps.get(order=5).poll
    agepoll = script.steps.get(order=6).poll
    genderpoll = script.steps.get(order=7).poll
    villagepoll = script.steps.get(order=8).poll
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
        else:
            contact.gender = 'F'

    village = find_best_response(session, villagepoll)
    if village:
        contact.village = find_closest_match(village, Location.objects)

    group = find_best_response(session, youthgrouppoll)
    default_group = None
    if Group.objects.filter(name='Other uReporters').count():
        default_group = Group.objects.get(name='Other uReporters')
    if group:
        for g in re.findall(r'\w+', group):
            group = find_closest_match(g, Group.objects)
            if group:
                break
        if group:
            contact.groups.add(group)
        elif default_group:
            contact.groups.add(default_group)
    elif default_group:
        contact.groups.add(default_group)

    if not contact.name:
        contact.name = 'Anonymous User'
    contact.save()

script_progress_was_completed.connect(autoreg, weak=False)
