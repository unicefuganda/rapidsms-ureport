import rapidsms
import datetime

from rapidsms.apps.base import AppBase
from contact.models import Flag, MessageFlag
from poll.models import Poll
from django.db.models import Q
from script.models import Script, ScriptProgress
from rapidsms.models import Contact
import re
from django.conf import settings
from ureport.tasks import process_message
class App(AppBase):
    def handle (self, message):
        one_template = r"(.*\b(%s)\b.*)"
        OPT_IN_WORDS_LUO = getattr(settings, 'OPT_IN_WORDS_LUO', None)
        OPT_IN_WORDS_EN = getattr(settings, 'OPT_IN_WORDS', None)
        if OPT_IN_WORDS_LUO:
            opt_reg = re.compile(r"|".join(OPT_IN_WORDS_LUO), re.IGNORECASE)

        #dump new connections in Autoreg
        if not message.connection.contact and not ScriptProgress.objects.filter(
            script__slug__in=['ureport_autoreg', 'ureport_autoreg_luo','ureport_autoreg2', 'ureport_autoreg_luo2'],
            connection=message.connection).exists():
            match = opt_reg.search(message.text.lower())
            if match:
                prog = ScriptProgress.objects.create(script=Script.objects.get(pk="ureport_autoreg_luo2"),\
                                                     connection=message.connection)
                prog.language = "ach"
                prog.save()
            else:
                prog = ScriptProgress.objects.create(script=Script.objects.get(pk="ureport_autoreg2"),\
                                                     connection=message.connection)
                prog.language = "en"
                prog.save()

            return True
         #ignore subsequent join messages
        elif message.text.lower().strip() in OPT_IN_WORDS_LUO+OPT_IN_WORDS_EN:
            return True
        else
            return False
        return False
            #suspected to be delaying message processing and causing nginx to drop http requests to ureport
            #message flagging sfuff
#        else:
#            if hasattr(message, 'db_message'):
#                pk = message.db_message.pk
#            else:
#                pk=message.pk
#            if message.connection.contact:
#                process_message.delay(pk)
#            if message.connection.contact and message.connection.contact.language == "ach" and message.text.lower() == "english":
#                contact=message.connection.contact
#                contact.language="en"
#                contact.save()
#                return True
#
#        flags=Flag.objects.exclude(rule=None).exclude(rule_regex=None)
#        for flag in flags:
#            print flag.rule_regex
#        pattern_list=[[re.compile(flag.rule_regex, re.IGNORECASE),flag] for flag in flags if flag.rule ]
#        for reg in pattern_list:
#            match= reg[0].search(message.text)
#            if match:
#                MessageFlag.objects.create(message=message.db_message,flag=reg[1])
#
#        #if no rule_regex default to name this is just for backward compatibility ... it will soon die an unnatural death
#
#        flags = Flag.objects.filter(rule=None).values_list('name', flat=True).distinct()
#
#        w_regex = []
#        for word in flags:
#            w_regex.append(one_template % re.escape(str(word).strip()))
#        reg = re.compile(r"|".join(w_regex),re.IGNORECASE)
#        match = reg.search(message.text)
#        if match:
#            #we assume ureport is not the first sms app in the list so there is no need to create db_message
#            if hasattr(message, 'db_message'):
#                db_message = message.db_message
#                try:
#                    flag = Flag.objects.get(name=[d for d in list(match.groups()) if d][1])
#                except (Flag.DoesNotExist, IndexError):
#                    flag = None
#                MessageFlag.objects.create(message=db_message, flag=flag)
#        return False
