from django.core.management.base import BaseCommand
import traceback
import os
from script.models import ScriptSession
from ureport.settings import UREPORT_ROOT
from rapidsms.models import Contact,Connection
from poll.models import Response
from script.utils.handling import find_closest_match, find_best_response
import datetime
from django.contrib.auth.models import Group

from rapidsms.contrib.locations.models import Location
import re

class Command(BaseCommand):

    def handle(self, **options):
        try:

            #get contacts without a connection
            contacts=Contact.objects.filter(connection=None)
            contacts_pks=contacts.values_list('pk')

            #get poll responses which point to these contacts and re align

            responses=Response.objects.filter(contact__pk__in=contacts_pks)

            for response in responses:
                response.contact=response.message.connection.contact
                response.save()

            #get connections without a contact
            
            conns=Connection.objects.filter(contact=None)
            conns_sessions=ScriptSession.objects.filter(connection__in=conns)
            for session in conns_sessions:
                connection=session.connection
                connection.contact = Contact.objects.create(name='Anonymous User')
                connection.save()

                script=session.script

                youthgrouppoll = script.steps.get(order=1).poll
                districtpoll = script.steps.get(order=3).poll
                namepoll = script.steps.get(order=5).poll
                agepoll = script.steps.get(order=6).poll
                genderpoll = script.steps.get(order=7).poll
                villagepoll = script.steps.get(order=8).poll
                contact = connection.contact
                name = find_best_response(session, namepoll)
                if name:
                    contact.name = name[:100]
            
                contact.reporting_location = find_best_response(session, districtpoll)

                age = find_best_response(session, agepoll)
                if age and age < 100:
                    contact.birthdate = datetime.datetime.now() - datetime.timedelta(days=(365 * int(age)))

                gresps = session.responses.filter(response__poll=genderpoll, response__has_errors=False).order_by('-response__date')
                if gresps.count():
                    gender = gresps[0].response
                    if gender.categories.filter(category__name='male').count():
                        contact.gender = 'M'
                    elif gender.categories.filter(category__name='female').exists():
                        contact.gender = 'F'

                village = find_best_response(session, villagepoll)
                if village:
                    contact.village = find_closest_match(village, Location.objects.filter(type__slug="village"))

                group_to_match = find_best_response(session, youthgrouppoll)
                default_group = None

                if Group.objects.filter(name='Other uReporters').count():
                    default_group = Group.objects.get(name='Other uReporters')
                if group_to_match:
                    for g in re.findall(r'\w+', group_to_match):
                        if g:
                            group = find_closest_match(str(g), Group.objects)
                            if group:
                                contact.groups.add(group)
                                break

                    if default_group:
                        contact.groups.add(default_group)
                elif default_group:
                    contact.groups.add(default_group)


                
            conns2=Connection.objects.filter(contact=None)
            #now delete connection less contacts
            Contact.objects.filter(connection=None).delete()
            #go ahead and create contacts for all connections
            for conn in conns2:
                conn.contact = Contact.objects.create(name='Anonymous User')
                conn.save()

            


        except Exception, exc:
            print traceback.format_exc(exc)
