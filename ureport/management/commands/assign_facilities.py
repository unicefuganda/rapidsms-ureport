from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from script.models import ScriptSession,Script
import traceback
import re
from django.contrib.auth.models import Group, User
from script.utils.handling import find_closest_match
from rapidsms.contrib.locations.models import Location
from rapidsms_httprouter.models import Message, Connection
from poll.models import Poll
import difflib
class Command(BaseCommand):
    def handle(self, **options):
        
        try:
            p_messages=Poll.objects.get(pk=162).responses.all()

            facilities=eval(open("fac.json").read())
            for m in p_messages:
                m_txt=m.message.text.lower()
                contact=m.message.connection.contact
                matches=difflib.get_close_matches(m_txt, facilities)
                if matches:
                    if contact:
                        contact.health_facility=matches[0]
                        print contact.pk
                        contact.save()


        except Exception, exc:
            print traceback.format_exc(exc)
