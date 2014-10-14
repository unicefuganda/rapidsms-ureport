# -*- coding: utf-8 -*-
import logging
import os
import urllib
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.utils.datastructures import SortedDict
import requests
from contact.models import MessageFlag
from rapidsms.models import Contact
from poll.models import ResponseCategory
from ureport.models.models import UPoll as Poll, PollAttribute, SentToMtrac
from script.models import ScriptStep, Script
from django.db.models import Count
from .models import Ureporter, UreportContact
from unregister.models import Blacklist
from django.conf import settings
from rapidsms_httprouter.models import Message
from django.contrib.sites.models import Site
from rapidsms.models import Connection
from poll.models import gettext_db
from django.db.models import Q
import datetime
import re
from uganda_common.models import Access
from uganda_common.utils import ExcelResponse
from ureport.settings import UREPORT_ROOT

module_name = __name__
logger = logging.getLogger(module_name)


def send_to_mtrac(message):
    log = logger
    try:
            message = message.senttomtrac
            log.info("Already Sent message to Mtrac on %s" % message.sent_on)
            return True
    except SentToMtrac.DoesNotExist:
        pass
    params = {'message': "%s %s"  % (getattr(settings, 'MTRAC_KEYWORD', 'ureport'), message.text), 'sender': message.connection.identity,
                               'backend': getattr(settings, 'MTRAC_PUSH_BACKEND'),
                               'password': getattr(settings, 'MTRAC_ROUTER_PASSWORD')}
    response = requests.get(getattr(settings, 'MTRAC_ROUTER_URL'), params=params)
    log.info("Request Url: %s" % response.url)
    if response.status_code in [200, 201]:
        SentToMtrac.objects.create(message=message)
        return True
    log.info("Message not sent returned code %d" % response.status_code)
    log.info("Response: %s " % response.text)
    return False


def get_access(request):
    try:
        access = Access.objects.get(user=request.user)
    except Access.DoesNotExist:
        access = None
    return access


def get_contacts(**kwargs):
    request = kwargs.pop('request')
    if request.user.is_authenticated() and hasattr(Contact, 'groups'):

        return Ureporter.objects.filter(groups__in=request.user.groups.all()).distinct().annotate(
            Count('responses')).select_related()
    else:
        return Ureporter.objects.annotate(Count('responses')).select_related()


def get_contacts2(**kwargs):
    request = kwargs.pop('request')
    if request.user.is_authenticated() and request.user.is_superuser:
        return UreportContact.objects.all()
    elif request.user.is_authenticated() and hasattr(Contact, 'groups'):
        q = None
        for f in request.user.groups.values_list('name', flat=True):
            if not q:
                q = Q(group__icontains=f)
            else:
                q = q | Q(group__icontains=f)

        try:
            to_ret = UreportContact.objects.filter(q)
        except TypeError:
            to_ret = UreportContact.objects.none()
        return to_ret

    return UreportContact.objects.none()


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
    try:
        not_showing = list(
            PollAttribute.objects.get(key="viewable").values.filter(value='true').values_list('poll_id', flat=True))
        not_showing = Poll.objects.exclude(pk__in=not_showing)
    except PollAttribute.DoesNotExist:
        not_showing = []
    if pks == 'l':
        return [Poll.objects.exclude(pk__in=script_polls).exclude(pk__in=not_showing).latest('start_date')]

    else:
        return Poll.objects.filter(pk__in=[pks]).exclude(pk__in=script_polls)


def get_flagged_messages(**kwargs):
    return MessageFlag.objects.all()


def get_quit_messages(**kwargs):
    OPT_OUT_WORDS = getattr(settings, 'OPT_OUT_WORDS')
    opt_words = "|".join(OPT_OUT_WORDS)
    return Message.objects.filter(text__iregex=".*\m(%s)\y.*" % opt_words).exclude(
        text__iregex=".*\m(%s)\y.*" % "what|uganda|sex|Because|why|which|how|\?|community|Children|where|yes|no")


def get_unsolicitized_messages(**kwargs):
    OPT_IN_WORDS_LUO = getattr(settings, 'OPT_IN_WORDS_LUO')
    OPT_IN_WORDS_EN = getattr(settings, 'OPT_IN_WORDS')
    opt_reg = "|".join(OPT_IN_WORDS_LUO + OPT_IN_WORDS_EN)
    return Message.objects.filter(application="ureport", direction="I").exclude(
        text__iregex=".*\m(%s)\y.*" % opt_reg).exclude(application="poll")


def get_poll_messages(**kwargs):
    return Message.objects.filter(application='poll', direction="I")


def get_autoreg_messages(**kwargs):
    return Message.objects.filter(application="script", direction="I")


def create_poll(name, type, question, default_response, contacts, user, start_immediately=False):
    localized_messages = {}
    bad_conns = Blacklist.objects.values_list('connection__pk', flat=True).distinct()
    contacts = contacts.exclude(connection__in=bad_conns)
    poll = Poll.objects.create(name=name, type=type, question=question, default_response=default_response, user=user)
    for language in dict(settings.LANGUAGES).keys():
        if language == "en":
            """default to English for contacts with no language preference"""
            localized_contacts = contacts.filter(language__in=["en", ''])
        else:

            localized_contacts = contacts.filter(language=language)
        if localized_contacts:
            if start_immediately:
                messages = Message.mass_text(gettext_db(field=question, language=language),
                                             Connection.objects.filter(contact__in=localized_contacts).distinct(),
                                             status='Q', batch_status='Q')
            else:
                messages = Message.mass_text(gettext_db(field=question, language=language),
                                             Connection.objects.filter(contact__in=localized_contacts).distinct(),
                                             status='L', batch_status='L')

            poll.messages.add(*messages.values_list('pk', flat=True))

    if 'django.contrib.sites' in settings.INSTALLED_APPS:
        poll.sites.add(Site.objects.get_current())
    if start_immediately:
        poll.start_date = datetime.datetime.now()
        poll.save()
    return poll


def add_to_poll(poll, contacts):
    localized_messages = {}
    bad_conns = Blacklist.objects.values_list('connection__pk', flat=True).distinct()
    contacts = contacts.exclude(connection__in=bad_conns)
    for language in dict(settings.LANGUAGES).keys():
        if language == "en":
            """default to English for contacts with no language preference"""
            localized_contacts = contacts.filter(language__in=["en", ''])
        else:

            localized_contacts = contacts.filter(language=language)
        if localized_contacts:
            messages = Message.mass_text(gettext_db(field=poll.question, language=language),
                                         Connection.objects.filter(contact__in=localized_contacts).distinct(),
                                         status='Q', batch_status='Q')

            localized_messages[language] = [messages, localized_contacts]



            # This is the fastest (pretty much only) was to get contacts and messages M2M into the
            # DB fast enough at scale
            #    cursor = connection.cursor()
            #    for language in localized_messages.keys():
            #        raw_sql = "insert into poll_poll_contacts (poll_id, contact_id) values %s" % ','.join(\
            #            ["(%d, %d)" % (poll.pk, c.pk) for c in localized_messages.get(language)[1].iterator()])
            #        cursor.execute(raw_sql)
            #
            #        raw_sql = "insert into poll_poll_messages (poll_id, message_id) values %s" % ','.join(\
            #            ["(%d, %d)" % (poll.pk, m.pk) for m in localized_messages.get(language)[0].iterator()])
            #        cursor.execute(raw_sql)

    return poll


def reprocess_none(poll):
    responses = poll.responses.filter(categories__category=None)
    for resp in responses:
        resp.has_errors = False
        for category in poll.categories.all():
            for rule in category.rules.all():
                regex = re.compile(rule.regex, re.IGNORECASE)
                if resp.eav.poll_text_value:
                    if regex.search(resp.eav.poll_text_value.lower()) and not resp.categories.filter(
                            category=category).count():
                        if category.error_category:
                            resp.has_errors = True
                        rc = ResponseCategory.objects.create(response=resp, category=category)
                        break
        if not resp.categories.all().count() and poll.categories.filter(default=True).count():
            if poll.categories.get(default=True).error_category:
                resp.has_errors = True
            resp.categories.add(
                ResponseCategory.objects.create(response=resp, category=poll.categories.get(default=True)))
        resp.save()


def fb(req, poll):
    import urllib2
    import urllib
    import json
    from ureport.models import Settings

    fb_settings = ['fb_page_id, fb_app_id, fb_app_secret, fb_url']
    setting = []
    for fbs in fb_settings:
        try:
            setting[fbs] = Settings.objects.get(attribute=fbs)
        except:
            setting[fbs] = None

    question = poll.question
    if poll.category_poll:
        options = json.dumps(poll.categories.all().values_list('name', flat=True))

    code = req.POST.get("code")

    if not code:
        # manage_pages permissions is required for accounts the user
        # has access to, and posting to the Page
        dialog_url = "http://www.facebook.com/dialog/oauth?client_id=%s&redirect_uri=%s&scope=manage_pages" % (
            setting['fb_app_id'], urllib.urlencode(setting['fb_url']))
        toret = '<script>top.location.href="%s";</script>' % dialog_url
    else:
        token_url = "https://graph.facebook.com/oauth/access_token?client_id=%s&redirect_uri=%s&client_secret=%s&code=%s" % (
            setting['fb_app_id'], urllib.urlencode(setting['fb_url']), setting['fb_app_secret'], code)
        access_token = urllib2.urlopen(token_url)
        accounts_url = "https://graph.facebook.com/me/accounts?%s" % access_token
        response = urllib2.urlopen(accounts_url)

        #Parse the return value and get the array of accounts - this is
        #returned in the data[] array.
        resp_obj = json.loads(response)
        accounts = resp_obj['data']

        #Find the access token for the Page
        page_access_token = None
        for account in accounts:
            if account['id'] == setting['fb_page_id']:
                page_access_token = 'access_token=%s' % account['access_token']
                break

        #Post the question to the Page
        post_question_url = "https://graph.facebook.com/%s/questions?question=%s&options=%s&allow_new_options=false&method=post&%s" % (
            setting['fb_page_id'], urllib.urlencode(question), urllib.urlencode(options), page_access_token)

        toret = urllib2.urlopen(post_question_url)
        return toret


def configure_messages_for_script(script_name, messages_dict):
    try:
        script = Script.objects.get(slug=script_name)
        for step in script.steps.order_by('order'):
            message_for_step = messages_dict.get(step.order)
            if step.message and message_for_step:
                step.message = message_for_step
            elif message_for_step:
                step.poll.question = message_for_step
                step.poll.save()
            step.save()
        script.save()
    except Script.DoesNotExist:
        logger.debug("[%s] Script object with slug name %s not found." % (module_name, script_name))


def export_poll(poll):
    if poll.responses.exists():
        print 'Working'
        responses = poll.responses.all()
        response_data_list = []
        excel_file_path = \
            os.path.join(os.path.join(os.path.join(UREPORT_ROOT,
                                                   'static'), 'spreadsheets'),
                         'poll_%d.xlsx' % poll.pk)
        for response in responses:

            response_export_data = SortedDict()
            if response.contact:
                try:
                    response_export_data['ID'] = response.contact.connection_set.all()[0].pk
                except IndexError:
                    continue
            else:
                response_export_data['ID'] = ""

            response_export_data['message_pk'] = response.message.pk

            if response.contact and response.contact.language:
                response_export_data['language'] = response.contact.language
            else:
                response_export_data['language'] = "en"

            if response.contact and response.contact.gender:
                response_export_data['sex'] = \
                    response.contact.gender
            else:
                response_export_data['sex'] = 'N/A'
            if response.contact and response.contact.birthdate:

                response_export_data['age'] = \
                    (datetime.datetime.now()
                     - response.contact.birthdate).days / 365
            else:

                response_export_data['age'] = 'N/A'
            if response.contact \
                and response.contact.reporting_location:
                response_export_data['district'] = \
                    response.contact.reporting_location.name
            else:
                response_export_data['district'] = 'N/A'
            if response.contact and response.contact.village:
                response_export_data['village'] = \
                    response.contact.village_name
            else:
                response_export_data['village'] = 'N/A'
            if response.contact and response.contact.subcounty:
                response_export_data['subcounty'] = \
                    response.contact.subcounty.name
            else:
                response_export_data['subcounty'] = 'N/A'
            if response.contact \
                and response.contact.groups.count() > 0:
                gr = list(response.contact.groups.order_by('pk').values_list('name', flat=True))
                try:
                    response_export_data['group1'] = gr[0]
                except IndexError:
                    response_export_data['group1'] = "N/A"
                try:
                    response_export_data['group2'] = gr[1]
                except IndexError:
                    response_export_data['group2'] = "N/A"
                try:
                    response_export_data['group3'] = gr[2]
                except IndexError:
                    response_export_data['group3'] = "N/A"

                response_export_data['groups'] = \
                    ','.join([group.name for group in
                              response.contact.groups.all()])
            else:
                response_export_data['groups'] = 'N/A'
                response_export_data['group1'] = response_export_data['group2'] = response_export_data[
                    'group3'] = 'N/A'
            if response.message:
                response_export_data['response'] = \
                    response.message.text
                response_export_data['date'] = \
                    response.message.date.strftime("%Y-%m-%d")
                response_export_data['time'] = \
                    response.message.date.strftime("%H:%M:%S")
            else:

                response_export_data['response'] = ''
                response_export_data['date'] = ''
                response_export_data['time'] = ''
            if response.poll:
                response_export_data['question'] = \
                    response.poll.question
            else:
                response_export_data['question'] = ''

            if response.categories.all().exists():
                response_export_data['category'] = response.categories.all()[0].category.name
            else:
                response_export_data['category'] = "uncategorized"

            response_data_list.append(response_export_data)
        ExcelResponse(response_data_list, output_name=excel_file_path, write_to_file=True)


def alert_if_mp(message):
    try:
        logger.debug("Checking if user is MP")
        mp_group = Group.objects.get(name=getattr(settings, 'MP_GROUP', 'MP'))
        if message.connection.contact.groups.filter(pk=mp_group.pk).exists():
            send_mail('Mp Alerts - From ID: %d' % message.connection.pk, message.text, "",
                      getattr(settings, 'PROJECT_MANAGERS', ('erikfrisk01@gmail.com', 'kbonky@gmail.com')))
    except Exception as e:
        logger.debug("Something wrong happened while alerting on MPs:" + str(e))