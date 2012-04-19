import re
from poll.models import STARTSWITH_PATTERN_TEMPLATE
import difflib
from poll.models import Poll, Response, ResponseCategory
from rapidsms.contrib.locations.models import Location
from django.core.management.base import BaseCommand
from eav.models import Attribute
from django.core.exceptions import ValidationError
from django.db import transaction
from rapidsms.models import Connection
import datetime

class Command(BaseCommand):


    def handle(self, **options):
        polls=Poll.objects.filter(categories__name__in=['yes','no'])
        for poll in polls:
            poll_responses=poll.responses.all()
            connections=Connection.objects.filter(pk__in=poll_responses.values_list('message__connection').distinct())
            for connection in connections:
                resp=poll.responses.filter(message__connection=connection,has_errors=False).order_by('-pk')
                if resp.count()>=2:
                    for d in resp[1:]:
                        print d
                        d.delete()




