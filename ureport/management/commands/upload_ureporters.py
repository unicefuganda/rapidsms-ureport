import os
import pwd
import traceback
from optparse import OptionParser, make_option
import datetime

from django.core.management.base import BaseCommand
from code_generator.code_generator import generate_tracking_tag
from simple_locations.models import Area,AreaType, Point
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
from ureport.models import find_closest_match

PREFIXES = [('70', 'warid'), ('75', 'zain'), ('71', 'utl'), ('', 'dmark')]

def assign_backend(number):
    if number.startswith('0') or len(number) == 9:
        number = '256%s' % number[1:]
    backendobj = None
    for prefix, backend in PREFIXES:
        if number[3:].startswith(prefix):
            backendobj, created = Backend.objects.get_or_create(name=backend)
            break
    return (number, backendobj)

class Command(BaseCommand):

    help = """loads all the districts from a csv, tab-delimited with "name type parent type [lat lon]"
    """
    option_list = BaseCommand.option_list + (
    make_option("-f", "--file", dest="path"),
    make_option("-g","--group", dest="group"),
    )

    def handle(self, **options):
        path=options["path"]
        group=options["group"]
        if group:
            group = find_closest_match(group, Group.objects)
        csv_rows = csv.reader(open(path), delimiter="\t")
        rnum = 0
        for row in csv_rows:
            if len(row) > 6:
                row = row[:6]
            district, village, name, phones, birthdate, gender = tuple(row)
            connections = []
            for raw_num in phones.split(','):
                number, backend = assign_backend(raw_num.replace('-','').strip())
                connection, created = Connection.objects.get_or_create(identity=number, backend=backend)
                connections.append(connection)
            
            name = ' '.join([n.capitalize() for n in name.lower().split(' ')])
            contact = Contact.objects.create(name=name)
            if group:
                contact.groups.add(group)
            if district:
                contact.reporting_location = find_closest_match(district, Area.objects.filter(kind__name='district'))
            if village:
                contact.village = find_closest_match(village, Area.objects)
            if birthdate:
                print "%d: %s" % (rnum, birthdate)
                contact.birthdate = datetime.datetime.strptime(birthdate.strip(),'%d/%m/%Y')
            if gender:
                contact.gender = gender
            contact.save()
            for c in connections:
                c.contact = contact
                c.save()
            rnum = rnum + 1
