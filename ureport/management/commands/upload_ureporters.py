import os
import pwd
import traceback
from optparse import OptionParser, make_option
import datetime

from django.core.management.base import BaseCommand
from rapidsms.contrib.locations.models import Location
from django.template.defaultfilters import slugify
from django.db import IntegrityError
from mptt.exceptions import InvalidMove
from django.shortcuts import get_object_or_404
from script.models import *
from script.signals import script_progress_was_completed
import csv
from django.contrib.auth.models import Group

from rapidsms.models import Backend, Connection, Contact
from poll.models import *
from script.utils.handling import find_closest_match

from uganda_common.utils import assign_backend

class Command(BaseCommand):

    help = """loads all the districts from a csv, tab-delimited with "name type parent type [lat lon]"
    """
    option_list = BaseCommand.option_list + (
    make_option("-f", "--file", dest="path"),
    make_option("-g", "--group", dest="group"),
    )

    def handle(self, **options):
        path = options["path"]
        gr = options["group"]

        group = find_closest_match(gr, Group.objects)
        print group
        csv_rows = csv.reader(open(path), delimiter=",")
        rnum = 0
        for row in csv_rows:

            name,mobile,sex,birthdate,district,village,sub_county,gr = tuple(row)
            if name=="name":
                continue

            number, backend = assign_backend(mobile.replace('-', '').strip())
            connection, created = Connection.objects.get_or_create(identity=number, backend=backend)
            if not created:
                contact = connection.contact
                if not contact:
                    contact = Contact.objects.create(name=name)
            else:
                contact = Contact.objects.create(name=name)

            if group:
                contact.groups.add(group)
            if district:
                try:
                    contact.reporting_location = find_closest_match(district, Location.objects.filter(type__name='district'))
                except:
                    contact.reporting_location = Location.objects.filter(type__name="district",name=district)[0]

            if village:
                contact.village = find_closest_match(village, Location.objects.filter(type__name='village'))
            if birthdate:

                contact.birthdate = datetime.datetime.strptime(birthdate.strip(), '%d/%m/%Y')
            if sex == "Male":
                contact.gender = "M"
            elif sex == "Female":
                contact.gender ="F"
            contact.save()

            connection.contact = contact
            connection.save()
            
