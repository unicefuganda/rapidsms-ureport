import os
import pwd
import traceback
from optparse import OptionParser, make_option
import datetime

from django.core.management.base import BaseCommand
from rapidsms.contrib.locations.models import Location,LocationType
from django.template.defaultfilters import slugify
from django.db import IntegrityError
from mptt.exceptions import InvalidMove
from django.shortcuts import get_object_or_404
from django.core.exceptions import MultipleObjectsReturned
import csv


class Command(BaseCommand):

    help = """
    """
    option_list = BaseCommand.option_list + (
    make_option("-f", "--file", dest="path"),
    )

    def handle(self, **options):
        path = options["path"]
        csv_rows = csv.reader(open(path,'rU'), delimiter=",")
        rnum = 0
        ug=Location.tree.root_nodes()[0]
        d_type=LocationType.objects.get(name="district")
        v_type=LocationType.objects.get(name="village")
        s_type=LocationType.objects.get(name="sub_county")
        for row in csv_rows:

            
            district_s,county_s,subcounty_s,parish_s,village_s = tuple(row)

            
            
            district=None
            subcounty=None
            village=None


            try:
                
                district=Location.objects.get(type=d_type,name=district_s.strip().lower().title())

            except Location.DoesNotExist:
                tocreate_district=Location(type=d_type,name=district_s.strip().lower().title())
                district=Location.tree.insert_node(tocreate_district, ug)
                district.save()
                print district_s
            except MultipleObjectsReturned:
                district=Location.objects.filter(type=d_type,name=district_s.strip().lower().title())[0]
                print "double" +district_s

            try:
                subcounty=district.children.get(type=s_type,name=subcounty_s.strip().lower().title())
            
            except Location.DoesNotExist:
                tocreate_subcounty=Location(type=s_type,name=subcounty_s.strip().lower().title())
                subcounty=Location.tree.insert_node(tocreate_subcounty, district)
                subcounty.parent=district
                subcounty.save()
                print subcounty_s

            try:
                village=district.children.get(type=v_type,name=village_s.strip().lower().title())
                if not village.get_ancestors():
                    #village.parent=None
                    #village.save()

                    print village_s
                    vill=Location.objects.get(pk=village.pk)
                    vill.move_to(subcounty, 'first-child')
                    vill.save()
            except Location.DoesNotExist:
                tocreate_village=Location(type=v_type,name=village_s.strip().lower().title())
                village=Location.tree.insert_node(tocreate_village, subcounty)
                village.parent=subcounty
                village.save()
                print village_s

           
            


