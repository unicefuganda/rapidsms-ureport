import re
from poll.models import STARTSWITH_PATTERN_TEMPLATE
import difflib
from poll.models import Poll, Response, ResponseCategory
from rapidsms.contrib.locations.models import Location
from django.core.management.base import BaseCommand
from eav.models import Attribute
from django.core.exceptions import ValidationError
from django.db import transaction
import datetime

class Command(BaseCommand):

    @transaction.commit_manually
    def handle(self, **options):
        polls=Poll.objects.filter(categories__name__in=['yes','no'])
        for poll in polls:
            poll_responses=poll.responses.all()
            connections=poll_responses.values_list('message__connection').distinct()
            poll.responses.filter(contact=message.connection.contact)

        for resp in Response.objects.all():
            num = num + 1
            if num % 100 == 0:
                td = datetime.datetime.now() - start
                td = float(td.seconds)
                est_time = ((td / num) * total) - td
                print "%d / %d (%d)" % (num, total, est_time)
                transaction.commit()
            message = resp.message
            if (resp.poll.type == Poll.TYPE_TEXT) and not resp.eav.poll_text_value:
                resp.eav.poll_text_value = resp.message.text
            elif (resp.poll.type == Poll.TYPE_LOCATION):
                if not resp.eav.poll_location_value:
                    location_template = STARTSWITH_PATTERN_TEMPLATE % '[a-zA-Z]*'
                    regex = re.compile(location_template)
                    if regex.search(message.text):
                        spn = regex.search(message.text).span()
                        location_str = message.text[spn[0]:spn[1]]
                        area = None
                        area_names = Location.objects.all().values_list('name', flat=True)
                        area_names_lower = [ai.lower() for ai in area_names]
                        area_names_matches = difflib.get_close_matches(location_str.lower(), area_names_lower)
                        if area_names_matches:
                            area = Location.objects.filter(name__iexact=area_names_matches[0])[0]
                            resp.eav.poll_location_value = area
                        resp.save()
                    else:
                        resp.has_errors = True

                else:
                    resp.has_errors = True

            elif (resp.poll.type == Poll.TYPE_NUMERIC):
                if not resp.eav.poll_number_value:
                    try:
                        regex = re.compile(r"(-?\d+(\.\d+)?)")
                        #split the text on number regex. if the msg is of form
                        #'19'or '19 years' or '19years' or 'age19'or 'ugx34.56shs' it returns a list of length 4
                        msg_parts = regex.split(message.text)
                        if len(msg_parts) == 4 :

                            resp.eav.poll_number_value = float(msg_parts[1])
                        else:
                            resp.has_errors = True
                    except IndexError:
                        resp.has_errors = True

            resp.save()
        transaction.commit()
