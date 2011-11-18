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

class App (AppBase):

    def handle (self, message):
        one_template = r"(.*\b(%s)\b.*)"
        OPT_IN_WORDS = getattr(settings,'OPT_IN_WORDS_LUO',None)
        if OPT_IN_WORDS:
            opt_reg = re.compile(r"|".join(OPT_IN_WORDS),re.IGNORECASE)


        if not message.connection.contact and not ScriptProgress.objects.filter(script__slug='ureport_autoreg', connection=message.connection).exists() and not ScriptProgress.objects.filter(script__slug='ureport_autoreg', connection=message.connection).exists():

            match = opt_reg.search(message.text)
            if match:
                prog=ScriptProgress.objects.create(script=Script.objects.get(pk="ureport_autoreg_luo"), \
                                          connection=message.connection)
                prog.language="ach"
                prog.save()
            else:
                prog=ScriptProgress.objects.create(script=Script.objects.get(pk="ureport_autoreg"), \
                                          connection=message.connection)
                prog.language="en"
                prog.save()
            
            return True
        flags = Flag.objects.values_list('name', flat=True).distinct()

        w_regex = []
        for word in flags:
            w_regex.append(one_template % str(word).strip())
        reg = re.compile(r"|".join(w_regex))
        match = reg.search(message.text)
        print match
        if match:
            #we assume ureport is not the first sms app in the list so there is no need to create db_message
            if hasattr(message, 'db_message'):
                db_message = message.db_message
                try:
                    flag = Flag.objects.get(name=[d for d in list(match.groups()) if d][1])
                except (Flag.DoesNotExist,IndexError):
                    flag = None
                MessageFlag.objects.create(message=db_message, flag=flag)
        return False
