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


    option_list = BaseCommand.option_list + (
    make_option("-f", "--file", dest="path"),

    )

    def handle(self, **options):
        path = options["path"]

        csv_rows = csv.reader(open(path), delimiter=",")
        rnum = 0
        for row in csv_rows[1:]:

            serial ,site_location,location,segment,district ,region  = tuple(row)
          

