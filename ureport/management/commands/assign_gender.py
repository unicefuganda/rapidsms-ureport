#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from script.models import ScriptSession,Script
import traceback
import re
from django.contrib.auth.models import Group, User
from script.utils.handling import find_closest_match
from rapidsms.contrib.locations.models import Location
from rapidsms_httprouter.models import Message, Connection
from rapidsms.models import Contact
from django.db.models import Q
class Command(BaseCommand):
    def handle(self, **options):
        #get gender_les
        no_gender_conns=Contact.objects.filter(gender=None).values_list('connection').distinct()

        messages=Message.objects.filter(connection__pk__in=no_gender_conns,direction="I").filter(Q(text="f")|Q(text="m")|Q(text="F")|Q(text="M")).order_by('date')
        try:
            for message in messages:
                contact=message.connection.contact
                print "yappy "+contact.name
                if message.text.lower()=="m":
                    contact.gender="M"
                elif message.text.lower() =="f":
                    contact.gender="F"
                contact.save()


        except Exception, exc:
            print traceback.format_exc(exc)
