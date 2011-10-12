import rapidsms
import datetime

from rapidsms.apps.base import AppBase
from .models import Poll, Flag, MessageFlag
from django.db.models import Q
from script.models import Script, ScriptProgress
from rapidsms.models import Contact
import re

class App (AppBase):

    def handle (self, message):
        if not message.connection.contact and not ScriptProgress.objects.filter(script__slug='ureport_autoreg', connection=message.connection).exists():
            ScriptProgress.objects.create(script=Script.objects.get(slug="ureport_autoreg"),\
                                          connection=message.connection)
            return True
        flags=Flag.objects.all()
        pattern_list=[[re.compile(flag.rule, re.IGNORECASE),flag] for flag in flags if flag.rule ]
        for reg in pattern_list:
            match= reg[0].search(message.text)
            if match:
                if hasattr(message, 'db_message'):
                    MessageFlag.objects.create(message=message.db_message,flag=reg[1])
            
        return False