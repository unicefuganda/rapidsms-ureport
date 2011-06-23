from django.db import models
from poll.models import Poll, LocationResponseForm, STARTSWITH_PATTERN_TEMPLATE
from rapidsms.models import Contact, Connection
from django.contrib.auth.models import User, Group
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.conf import settings
from simple_locations.models import Area, AreaType
from eav.models import Attribute
from django.core.exceptions import ValidationError
from script.signals import *
from script.models import *
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
    name=models.CharField(max_length=20)

    def __unicode__(self):
        return '%s'%self.name

class MassText(models.Model):
    sites = models.ManyToManyField(Site)
    contacts = models.ManyToManyField(Contact, related_name='masstexts')
    user = models.ForeignKey(User)
    date = models.DateTimeField(auto_now_add=True,null=True)
    text = models.TextField()
    objects = (CurrentSiteManager('sites') if settings.SITE_ID else models.Manager())
    bulk = BulkInsertManager()
    
    class Meta:
        permissions = (
            ("can_message", "Can send messages, create polls, etc"),
        )
        
class MessageFlag(models.Model):
    #Track flagged messages
    message = models.ForeignKey(Message, related_name='flags')

def parse_district_value(value):
    location_template = STARTSWITH_PATTERN_TEMPLATE % '[a-zA-Z]*'
    regex = re.compile(location_template)
    toret = find_closest_match(value, Area.objects.filter(kind__name='district'))
    if not toret:
        raise ValidationError("We didn't recognize your district.  Please carefully type the name of your district and re-send.")
    else:
        return toret

Poll.register_poll_type('district', 'District Response', parse_district_value, db_type=Attribute.TYPE_OBJECT,\
                        view_template='polls/response_location_view.html',
                        edit_template='polls/response_location_edit.html',
                        report_columns=(('Text','text'),('Location','location'),('Categories','categories')),
                        edit_form=LocationResponseForm)

def find_best_response(session, poll):
    resps = session.responses.filter(response__poll=poll, response__has_errors=False).order_by('-response__date')
    if resps.count():
        resp = resps[0].response
        typedef = Poll.TYPE_CHOICES[poll.type]
        if typedef['db_type'] == Attribute.TYPE_TEXT:
            return resp.eav.poll_text_value
        elif typedef['db_type'] == Attribute.TYPE_FLOAT:
            return resp.eav.poll_number_value
        elif typedef['db_type'] == Attribute.TYPE_OBJECT:
            return resp.eav.poll_location_value
    return None

def find_closest_match(value, model):
    string_template = STARTSWITH_PATTERN_TEMPLATE % '[a-zA-Z]*'
    regex = re.compile(string_template)
    try:
        if regex.search(value):
            spn = regex.search(value).span()
            name_str = value[spn[0]:spn[1]]
            toret = None
            model_names = model.values_list('name', flat=True)
            model_names_lower = [ai.lower() for ai in model_names]
            model_names_matches = difflib.get_close_matches(name_str.lower(), model_names_lower)
            if model_names_matches:
                toret = model.get(name__iexact=model_names_matches[0])
                return toret
    except:
        return None

def autoreg(**kwargs):
    connection = kwargs['connection']
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

    if not connection.contact:
        connection.contact = Contact.objects.create()
        connection.save
    contact = connection.contact

    name = find_best_response(session, namepoll)
    if name:
        contact.name = name[:100]

    contact.reporting_location = find_best_response(session, districtpoll)

    age = find_best_response(session, agepoll)
    if age and age < 100:
        contact.birthdate = datetime.datetime.now() - datetime.timedelta(days=(365*int(age)))

    gresps = session.responses.filter(response__poll=genderpoll, response__has_errors=False).order_by('-response__date')
    if gresps.count():
        gender = gresps[0].response
        if gender.categories.filter(category__name='male').count():
            contact.gender = 'M'
        else:
            contact.gender = 'F'

    village = find_best_response(session, villagepoll)
    if village:
        contact.village = find_closest_match(village, Area.objects)

    group = find_best_response(session, youthgrouppoll)
    default_group = None
    if Group.objects.filter(name='Other uReporters').count():
        default_group = Group.objects.get(name='Other uReporters')
    if group:
        group = find_closest_match(group, Group.objects)
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