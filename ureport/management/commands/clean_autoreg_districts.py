#!/usr/bin/python

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from script.models import ScriptSession,Script
import traceback
import re
from django.contrib.auth.models import Group, User
from script.utils.handling import find_closest_match
from rapidsms.contrib.locations.models import Location
from rapidsms_httprouter.models import Message, Connection
from django.db import DatabaseError,transaction
import re
class Command(BaseCommand):
    def handle(self, **options):
        no_district_connections=Connection.objects.filter(contact__reporting_location=None).values_list('pk',flat=True)
        sic="|".join(Location.objects.filter(type__name='district').values_list('name',flat=True))

        messages=Message.objects.filter(connection__pk__in=no_district_connections,direction="I").filter(text__iregex=".*\m(%s)\y.*"%sic).order_by('date')
        try:
            for message in messages:
                if message.connection.contact:
                    mesg=message.text
                    mesg=mesg.replace("."," ").replace("("," ").replace(")"," ").replace("-"," ").replace(":"," ").replace(","," ").replace("}"," ").replace("{"," ").replace("?"," ").replace("'"," ").replace("/"," ")
                    msg=mesg.split()


                    for m in msg:
                        try:
                            district=Location.objects.filter(name__iregex="\m(%s)\y"%re.escape(m),type="district")
                            if district:
                                pass
                            l=0
                        except:
                            try:
                                transaction.rollback()
                            except:
                                pass
                            continue
                        
                        l=int(district.count())
                       
                        if district and l == 1:

                            conn=message.connection
                            if not conn.contact.reporting_location:
                                contact=conn.contact
                                contact.reporting_location=district[0]
                                contact.save()
                            break
                    print message.text
                    print message.connection.contact.reporting_location

        except Exception, exc:
            print traceback.format_exc(exc)
            pass
