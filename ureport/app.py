from django.contrib.auth.models import Group
from django.core.mail import send_mail
from rapidsms.apps.base import AppBase
from contact.models import Flag, MessageFlag
from script.models import Script, ScriptProgress
import re
from django.conf import settings
from ureport.models import MessageAttribute, MessageDetail, Settings, FlagTracker

import logging
from rapidsms_httprouter.models import Message

log = logging.getLogger(__name__)


class App(AppBase):
    def handle(self, message):
        """

        :param message:
        :return:
        """
        if message.connection is not None and message.db_message is not None:
            log.debug("[ureport-app] [{}] Handling incoming message [pk={}]...".format(message.connection.identity,
                                                                                       message.db_message.pk))
        one_template = r"(.*\b(%s)\b.*)"
        OPT_IN_WORDS_LUO = getattr(settings, 'OPT_IN_WORDS_LUO', None)
        OPT_IN_WORDS_EN = getattr(settings, 'OPT_IN_WORDS', None)
        OPT_IN_WORDS_KDJ = getattr(settings, 'OPT_IN_WORDS_KDJ', None)


        if OPT_IN_WORDS_LUO:
            opt_reg_luo = re.compile(r"|".join(OPT_IN_WORDS_LUO), re.IGNORECASE)
        if OPT_IN_WORDS_KDJ:
            opt_reg_kdj = re.compile(r"|".join(OPT_IN_WORDS_KDJ), re.IGNORECASE)
        if OPT_IN_WORDS_EN:
            opt_reg_en = re.compile(r"|".join(OPT_IN_WORDS_EN), re.IGNORECASE)

        #dump new connections in Autoreg
        if not message.connection.contact and not \
            ScriptProgress.objects.filter(
                    script__slug__in=['ureport_autoreg2', 'ureport_autoreg_luo2', 'ureport_autoreg_kdj'], \
                    connection=message.connection).exists():

            log.debug("[ureport-app] [%s] No contact found, adding to registration" % message.connection.identity)
            prog = ScriptProgress.objects.create(script=Script.objects.get(pk="ureport_autoreg_luo2"), \
                                                     connection=message.connection)
            try:
                luo_match = opt_reg_luo.search(message.text.lower())
                if luo_match:
                    prog.language = "ach"
            except UnboundLocalError:
                pass
            try:
                kdj_match = opt_reg_kdj.search(message.text.lower())
                if kdj_match:
                    prog.language = "kdj"
            except UnboundLocalError:
                pass
            try:
                en_match = opt_reg_en.search(message.text.encode('utf-8'))
                if en_match:
                    prog.language = "en"
            except UnboundLocalError:
                pass
            prog.save()
            return True
            #ignore subsequent join messages
        elif message.text.encode('utf-8').lower().strip() in OPT_IN_WORDS_LUO + OPT_IN_WORDS_EN:
            if message.connection is not None:
                log.debug(
                    "[ureport-app] [%s] Contact has already registered, ignoring message" % message.connection.identity)
            return True
        #        else:
        #            return False
        #        return False
        #suspected to be delaying message processing and causing nginx to drop http requests to ureport
        #message flagging sfuff
        else:

            if message.connection.contact:
                alert_setting, _ = Settings.objects.get_or_create(attribute="alerts")
                try:
                    mp = Group.objects.get(name='MP')
                    if mp in message.connection.contact.groups.all():
                        log.info('MP with ID %d just sent in a message %s, emailing it to Erik' % (
                            message.connection_id, message.text))
                        send_mail('MP Sent Message to Ureport', message.text, "Ureport Alerts<alerts@ureport.ug>",
                                  ['Erikfrisk01@gmail.com'], fail_silently=True)
                except:
                    pass
                if alert_setting.value == "true":
                    log.debug(
                        "[ureport-app] [%s] because 'alerts' is true and this is Not a registration or a poll message, creating MessageDetail alert..." % message.connection.identity)
                    alert, _ = MessageAttribute.objects.get_or_create(name="alert")
                    msg_a = MessageDetail.objects.create(message=message.db_message, attribute=alert, value='true')
            if message.connection.contact and message.connection.contact.language == "ach" and message.text.lower() == "english":
                log.debug(
                    "[ureport-app] [%s] Changing language to en because contact language was 'ach'" % message.connection.identity)
                contact = message.connection.contact
                contact.language = "en"
                contact.save()
                return True
        if message.connection is not None:
            log.debug("[ureport-app] [%s] Checking for flags..." % message.connection.identity)
        flags = Flag.objects.exclude(rule=None).exclude(rule_regex=None)

        pattern_list = [[re.compile(flag.rule_regex, re.IGNORECASE), flag] for flag in flags if flag.rule]
        for reg in pattern_list:
            match = reg[0].search(message.text)
            if match:
                if hasattr(message, 'db_message'):
                    msg = message.db_message
                else:
                    msg = message
                mf = MessageFlag.objects.create(message=msg, flag=reg[1])
                log.info(mf)

        #if no rule_regex default to name this is just for backward compatibility ... it will soon die an unnatural death

        flags = Flag.objects.filter(rule=None).values_list('name', flat=True).distinct()

        w_regex = []
        for word in flags:
            w_regex.append(one_template % re.escape(str(word).strip()))
        reg = re.compile(r"|".join(w_regex), re.IGNORECASE)
        match = reg.search(message.text)
        if match:
            #we assume ureport is not the first sms app in the list so there is no need to create db_message
            if hasattr(message, 'db_message'):
                db_message = message.db_message
                try:
                    flag = Flag.objects.get(name=[d for d in list(match.groups()) if d][1])
                except (Flag.DoesNotExist, IndexError):
                    flag = None
                MessageFlag.objects.create(message=db_message, flag=flag)
                if message.connection is not None:
                    log.debug("[ureport-app] [{}] Created MessageFlag".format(message.connection.identity))
        if message.connection is not None:
            log.debug("[ureport-app] [%s] Completed handling of incoming message." % message.connection.identity)
            if FlagTracker.objects.filter(response=None, message__connection=message.connection).exists():
                tracker = FlagTracker.objects.filter(response=None, message__connection=message.connection).order_by(
                    '-reply__date')[0]
                if not Message.objects.filter(connection=message.connection, date__gt=tracker.reply.date,
                                              direction='O').exists():
                    tracker.response = message
                    tracker.save()
        return False