import rapidsms
import datetime

from rapidsms.apps.base import AppBase
from .models import Poll
from django.db.models import Q
from script.models import Script, ScriptProgress

class App (AppBase):
    
    def handle (self, message):
        if not message.connection.contact:
            message.connection.contact = Contact.objects.create(name='Anonymous User')
            message.connection.save()
            ScriptProgress.objects.create(script=Script.objects.get(slug="ureport_autoreg"),\
                                          connection=message.connection)
            return True
        return False