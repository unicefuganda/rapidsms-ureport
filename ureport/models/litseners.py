# -*- coding: utf-8 -*-
import simplejson as json
import requests
from rapidsms.models import Contact, Connection
from script.models import ScriptSession
from rapidsms_xforms.models import XFormField
import datetime
from script.utils.handling import find_closest_match, find_best_response
from django.contrib.auth.models import Group
from unregister.models import Blacklist
from ussd.models import Menu, StubScreen
import re
from models import AutoregGroupRules, EquatelLocation
from .utils import update_poll_results
from poll.models import ResponseCategory, Response, Poll
from rapidsms_httprouter.models import Message
from django.conf import settings
from django.core.mail import send_mail
import logging


log = logging.getLogger(__name__)

def autoreg(**kwargs):
    connection = kwargs['connection']
    progress = kwargs['sender']
    if progress.script.slug and progress.script.slug in ['ureport_autoreg2', 'ureport_autoreg_luo2']:
        connection.contact = Contact.objects.create(name='Anonymous User')
        connection.save()
        session = ScriptSession.objects.filter(script=progress.script, connection=connection).order_by('-end_time')[0]
        script = progress.script
        youthgrouppoll = script.steps.get(order=1).poll
        districtpoll = script.steps.get(order=2).poll
        agepoll = script.steps.get(order=4).poll
        genderpoll = script.steps.get(order=5).poll
        villagepoll = script.steps.get(order=6).poll
        contact = connection.contact
        word_dict = dict(
            AutoregGroupRules.objects.exclude(values=None).exclude(closed=True).values_list('group__name', 'values'))

        contact.reporting_location = find_best_response(session, districtpoll)

        age = find_best_response(session, agepoll)
        if age and age < 100:
            contact.birthdate = datetime.datetime.now() - datetime.timedelta(days=(365 * int(age)))

        gresps = session.responses.filter(response__poll=genderpoll, response__has_errors=False).order_by(
            '-response__date')
        if gresps.exists():
            gender = gresps[0].response
            if gender.categories.filter(category__name='male').exists():
                contact.gender = 'M'
            elif gender.categories.filter(category__name='female').exists():
                contact.gender = 'F'

        village = find_best_response(session, villagepoll)
        if village:
            contact.village_name = village

        group_to_match = find_best_response(session, youthgrouppoll)
        gr_matched = False

        #to avoid an attempt to None.split()
        if group_to_match:
            try:
                for group_pk, word_list in word_dict.items():
                    for word in word_list.split(","):
                        if word in group_to_match.split():
                            try:
                                contact.groups.add(Group.objects.get(name=group_pk))
                            except (ValueError, Group.DoesNotExist):
                                try:
                                    contact.groups.add(Group.objects.get(pk=group_pk))
                                except (ValueError, Group.DoesNotExist):
                                    pass
                            gr_matched = True
            except AssertionError:
                pass
        default_group = None
        if progress.language:
            contact.language = progress.language
        if Group.objects.filter(name='Other uReporters').exists():
            default_group = Group.objects.get(name='Other uReporters')
        if group_to_match and not gr_matched:

            for g in re.findall(r'\w+', group_to_match):
                if g:
                    excluded = AutoregGroupRules.objects.filter(closed=True).values('group__pk')
                    group = find_closest_match(str(g), Group.objects.exclude(pk__in=excluded))
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

        total_ureporters = Contact.objects.exclude(
            connection__identity__in=Blacklist.objects.values_list('connection__identity')).count()
        if total_ureporters % getattr(settings, 'USER_MILESTONE', 500) == 0:
            recipients = getattr(settings, 'ADMINS', None)
            if recipients:
                recipients = [email for name, email in recipients]
            mgr = getattr(settings, 'MANAGERS', None)
            if mgr:
                for email in mgr:
                    recipients.append(email)
            send_mail("UReport now %d voices strong!" % total_ureporters,
                      "%s (%s) was the %dth member to finish the sign-up.  Let's welcome them!" % (
                          contact.name, connection.identity, total_ureporters), 'root@uganda.rapidsms.org', recipients,
                      fail_silently=True)


def check_conn(sender, **kwargs):
    #delete bad connections
    c = kwargs['instance']
    if not c.identity.isdigit():
        c.delete()
        return True


def update_latest_poll(sender, **kwargs):
    poll = kwargs['instance']
    if poll.categories.filter(name__in=['yes', 'no']):
        try:
            xf = XFormField.objects.get(name='latest_poll', command="poll_" + str(poll.pk))
            xf.question = poll.question
            xf.command = "poll_" + str(poll.pk)
            xf.save()
            stub_screen = StubScreen.objects.get(slug='question_response')
            if poll.default_response:
                stub_screen.text = poll.default_response
                stub_screen.save()
            else:
                stub_screen.text = "Thanks For Your Response."
                stub_screen.save()
            update_poll_results()
        except (XFormField.DoesNotExist, StubScreen.DoesNotExist):
            pass

        try:
            Menu.tree.rebuild()
        except:
            pass


def ussd_poll(sender, **kwargs):
    connection = sender.connection
    if not sender.connection.contact:
        connection.contact = Contact.objects.create(name='Anonymous User')

        try:
            serial = sender.navigations.order_by('date')[1].response.rsplit("_")[0]
            connection.contact.reporting_location = EquatelLocation.objects.get(serial=serial).location
            connection.contact.save()
        except EquatelLocation.DoesNotExist:
            pass
        connection.save()
        equatel, created = Group.objects.get_or_create(name="equatel")
        connection.contact.groups.add(equatel)

    if sender.navigations.filter(screen__slug='weekly_poll').exists():
        field = XFormField.objects.get(name="latest_poll")
        nav = sender.navigations.filter(screen__slug='weekly_poll').latest('date')
        poll = Poll.objects.get(pk=int(field.command.rsplit('_')[1]))
        if poll.categories.filter(name__in=["yes", "no"]):
            yes = poll.categories.get(name="yes")
            no = poll.categories.get(name='no')
            cats = {'1': ['yes', yes], '2': ['no', no]}
            msg = Message.objects.create(connection=connection, text=cats[nav.response][0], direction="I")
            resp = Response.objects.create(poll=poll, message=msg, contact=connection.contact, date=nav.date)
            resp.categories.add(ResponseCategory.objects.create(response=resp, category=cats[nav.response][1]))
            #update results
    update_poll_results()

    if sender.navigations.filter(screen__slug='send_report'):
        Message.objects.create(connection=connection,
                               text=sender.navigations.filter(screen__slug='send_report').latest('date').response,
                               direction="I")


def add_to_poll(sender, **kwargs):
    try:
        contact = kwargs.get('instance').connection.contact
        poll = Poll.objects.get(name="blacklist")
        poll.contacts.add(contact)
    except:
        pass


def add_poll_to_blacklist(sender, **kwargs):
    url = getattr(settings,"BLACKLIST_POLL_DATA_URL", None)
    if url:
        poll = sender
        values = {'poll_id': str(poll.pk),
                  'poll_text': poll.question,
                  'poll_response': poll.default_response }
        log.info('[add_poll_to_blacklist] Poll id=%s, question=%s, response=%s' % (values["poll_id"], values['poll_text'], values["poll_response"]))
        try:
            response = requests.post(url, data=values)
            log.info('[add_poll_to_blacklist] Adding poll details to blacklist status:%s' % response.status_code)
        except Exception, e:
            log.error(e)

def add_poll_recipients_to_blacklist(sender, **kwargs):
    url = getattr(settings,"BLACKLIST_POLL_RECIPIENTS_URL", None)
    if url:
        poll = sender
        contacts = poll.contacts.all()
        values = Connection.objects.filter(contact__in=contacts).distinct().values_list('identity', flat=True)
        data = json.dumps(list(values))
        log.info('[add_poll_recipients_to_blacklist] Poll id=%s' % poll.pk)
        try:
            response = requests.post(url, data=data, params={"poll_id": poll.pk})
            log.info('[add_poll_recipients_to_blacklist] Adding poll recipients to blacklist-status:%s' % response.status_code)
        except Exception, e:
            log.error('[add_poll_recipients_to_blacklist] Error: %s' % e)