from django.core.management.base import BaseCommand
import traceback
from script.models import ScriptSession,ScriptProgress
from rapidsms.models import Contact
from script.utils.handling import find_closest_match, find_best_response
import datetime
from django.contrib.auth.models import Group

from rapidsms.contrib.locations.models import Location
import re
class Command(BaseCommand):
    def handle(self, **options):
        try:

            sp=ScriptProgress.objects.values_list('connection',flat=True)
            scriptsessions=ScriptSession.objects.exclude(connection__in=sp)

            for session in scriptsessions:
                connection=session.connection
                script = session.script
                youthgrouppoll = script.steps.get(order=1).poll
                districtpoll = script.steps.get(order=3).poll
                namepoll = script.steps.get(order=5).poll
                agepoll = script.steps.get(order=6).poll
                genderpoll = script.steps.get(order=7).poll
                villagepoll = script.steps.get(order=8).poll
                contact = connection.contact
                name = find_best_response(session, namepoll)
                district = find_best_response(session, districtpoll)
                
                if name:
                    contact.name = name[:100]
                    print "original name" +contact.name
                    print name


                contact.reporting_location = district


                age = find_best_response(session, agepoll)
                if age and age < 100:
                    contact.birthdate = datetime.datetime.now() - datetime.timedelta(days=(365 * int(age)))

                gresps = session.responses.filter(response__poll=genderpoll, response__has_errors=False).order_by('-response__date')
                if gresps.count():
                    gender = gresps[0].response
                    print "original gender"
                    print contact.gender
                    print gender
                    if gender.categories.filter(category__name='male').count():
                        contact.gender = 'M'
                    elif gender.categories.filter(category__name='female').exists():
                        contact.gender = 'F'
                    else:
                        contact.gender=None

                village = find_best_response(session, villagepoll)
                if village:
                    print str(contact.village) + "->" +str(village)
                    contact.village = find_closest_match(village, Location.objects.filter(type__slug="village"))


                contact.save()

               

       
        except Exception, exc:
            print traceback.format_exc(exc)
