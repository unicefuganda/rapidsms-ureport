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
from rapidsms_httprouter.models import Message, MessageBatch
from unregister.models import Blacklist
from django.db.models.signals import post_save
from django.conf import settings
from django.core.mail import send_mail

import datetime
import re
import difflib


class IgnoredTags(models.Model):
    poll = models.ForeignKey(Poll)
    name = models.CharField(max_length=20)

    def __unicode__(self):
        return '%s' % self.name


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
    progress = kwargs['sender']
    if not progress.script.slug == 'ureport_autoreg':
        return

    connection.contact = Contact.objects.create(name='Anonymous User')
    connection.save()
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

    group_to_match = find_best_response(session, youthgrouppoll)
    default_group = None
    if Group.objects.filter(name='Other uReporters').count():
        default_group = Group.objects.get(name='Other uReporters')
    if group_to_match:
        for g in re.findall(r'\w+', group_to_match):
            group = find_closest_match(g, Group.objects)
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


def bulk_blacklist(sender, **kwargs):
    """
    This method optimizes the handling of blacklisted numbers.  Normally,
    messages would have to be checked one by one, using the outgoing() methods
    of all SMS_APPS.  However, with UReport, the only app that actually uses outgoing()
    is unregister, and this method handles doing this process for all messages at once
    """
    if sender == Poll:
        poll = kwargs['instance']
        if poll.start_date:
            bad_conns = Blacklist.objects.values_list('connection__pk', flat=True).distinct()
            bad_conns = Connection.objects.filter(pk__in=bad_conns)
            poll.messages.filter(status='P').exclude(connection__in=bad_conns).update(status='Q')
    elif sender == MessageBatch:
        batch = kwargs['instance']
        bad_conns = Blacklist.objects.values_list('connection__pk', flat=True).distinct()
        bad_conns = Connection.objects.filter(pk__in=bad_conns)
        batch.messages.filter(status='P').exclude(connection__in=bad_conns).update(status='Q')


script_progress_was_completed.connect(autoreg, weak=False)
post_save.connect(bulk_blacklist, weak=False)
