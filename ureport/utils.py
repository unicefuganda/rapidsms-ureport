# -*- coding: utf-8 -*-
from contact.models import MessageFlag
from rapidsms.models import Contact
from poll.models import Poll,ResponseCategory
from script.models import ScriptStep
from django.db.models import Count
from .models import Ureporter
from unregister.models import Blacklist
from django.conf import settings
from rapidsms_httprouter.models import Message, MessageBatch
from django.contrib.sites.models import Site
from rapidsms.models import Contact, Connection
from django.db import models, transaction, connection
from poll.models import gettext_db
import datetime
import re

def get_contacts(**kwargs):
    request = kwargs.pop('request')
    if request.user.is_authenticated() and hasattr(Contact, 'groups'):
        return Ureporter.objects.filter(groups__in=request.user.groups.all()).distinct().annotate(Count('responses'))
    else:
        return Ureporter.objects.annotate(Count('responses'))


def get_polls(**kwargs):
    script_polls = ScriptStep.objects.exclude(poll=None).values_list('poll', flat=True)
    return Poll.objects.exclude(pk__in=script_polls).annotate(Count('responses'))

def get_script_polls(**kwargs):
    script_polls = ScriptStep.objects.exclude(poll=None).values_list('poll', flat=True)
    return Poll.objects.filter(pk__in=script_polls).annotate(Count('responses'))

#def retrieve_poll(request):
#    pks=request.GET.get('pks', '').split('+')
#    if pks[0] == 'l':
#        return [Poll.objects.latest('start_date')]
#    else:
#        pks=[eval(x) for x in list(str(pks[0]).rsplit())]
#        return Poll.objects.filter(pk__in=pks)

def retrieve_poll(request, pks=None):
    script_polls = ScriptStep.objects.exclude(poll=None).values_list('poll', flat=True)
    if pks == None:
        pks = request.GET.get('pks', '')
    if pks == 'l':
        return [Poll.objects.exclude(pk__in=script_polls).latest('start_date')]
    else:
        return Poll.objects.filter(pk__in=[pks]).exclude(pk__in=script_polls)

def get_flagged_messages(**kwargs):

    return MessageFlag.objects.all()

def get_quit_messages(**kwargs):
    bl=Blacklist.objects.values_list('connection',flat=True).distinct()
    return Ureporter.objects.filter(connection__in=bl)


def create_poll(name, type, question, default_response, contacts, user,start_immediately=False):
    localized_messages = {}
    bad_conns = Blacklist.objects.values_list('connection__pk', flat=True).distinct()
    contacts=contacts.exclude(connection__in=bad_conns)
    for language in dict(settings.LANGUAGES).keys():
        if language == "en":
            """default to English for contacts with no language preference"""
            localized_contacts = contacts.filter(language__in=["en", ''])
        else:

            localized_contacts = contacts.filter(language=language)
        if localized_contacts.exists():
            if start_immediately:
                messages = Message.mass_text(gettext_db(field=question, language=language), Connection.objects.filter(contact__in=localized_contacts).distinct(), status='Q', batch_status='Q')
            else:
                messages = Message.mass_text(gettext_db(field=question, language=language), Connection.objects.filter(contact__in=localized_contacts).distinct(), status='L', batch_status='L')
            localized_messages[language] = [messages, localized_contacts]
    poll = Poll.objects.create(name=name, type=type, question=question, default_response=default_response, user=user)

        
    # This is the fastest (pretty much only) was to get contacts and messages M2M into the
    # DB fast enough at scale
    cursor = connection.cursor()
    for language in localized_messages.keys():
        raw_sql = "insert into poll_poll_contacts (poll_id, contact_id) values %s" % ','.join(\
            ["(%d, %d)" % (poll.pk, c.pk) for c in localized_messages.get(language)[1].iterator()])
        cursor.execute(raw_sql)

        raw_sql = "insert into poll_poll_messages (poll_id, message_id) values %s" % ','.join(\
            ["(%d, %d)" % (poll.pk, m.pk) for m in localized_messages.get(language)[0].iterator()])
        cursor.execute(raw_sql)

    if 'django.contrib.sites' in settings.INSTALLED_APPS:
        poll.sites.add(Site.objects.get_current())
    if start_immediately:
        poll.start_date = datetime.datetime.now()
        poll.save()
    return poll

def add_to_poll(poll,contacts):
    localized_messages = {}
    bad_conns = Blacklist.objects.values_list('connection__pk', flat=True).distinct()
    contacts=contacts.exclude(connection__in=bad_conns)
    for language in dict(settings.LANGUAGES).keys():
        if language == "en":
            """default to English for contacts with no language preference"""
            localized_contacts = contacts.filter(language__in=["en", ''])
        else:

            localized_contacts = contacts.filter(language=language)
        if localized_contacts.exists():
            messages = Message.mass_text(gettext_db(field=poll.question, language=language), Connection.objects.filter(contact__in=localized_contacts).distinct(), status='Q', batch_status='Q')

            localized_messages[language] = [messages, localized_contacts]



    # This is the fastest (pretty much only) was to get contacts and messages M2M into the
    # DB fast enough at scale
    cursor = connection.cursor()
    for language in localized_messages.keys():
        raw_sql = "insert into poll_poll_contacts (poll_id, contact_id) values %s" % ','.join(\
            ["(%d, %d)" % (poll.pk, c.pk) for c in localized_messages.get(language)[1].iterator()])
        cursor.execute(raw_sql)

        raw_sql = "insert into poll_poll_messages (poll_id, message_id) values %s" % ','.join(\
            ["(%d, %d)" % (poll.pk, m.pk) for m in localized_messages.get(language)[0].iterator()])
        cursor.execute(raw_sql)


    return poll

def reprocess_none(poll):
    responses=poll.responses.filter(categories__category=None)
    for resp in responses:
        resp.has_errors = False
        for category in poll.categories.all():
            for rule in category.rules.all():
                regex = re.compile(rule.regex, re.IGNORECASE)
                if resp.eav.poll_text_value:
                    if regex.search(resp.eav.poll_text_value.lower()) and not resp.categories.filter(category=category).count():
                        if category.error_category:
                            resp.has_errors = True
                        rc = ResponseCategory.objects.create(response=resp, category=category)
                        break
        if not resp.categories.all().count() and poll.categories.filter(default=True).count():
            if poll.categories.get(default=True).error_category:
                resp.has_errors = True
            resp.categories.add(ResponseCategory.objects.create(response=resp, category=poll.categories.get(default=True)))
        resp.save()

