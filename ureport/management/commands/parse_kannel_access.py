#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from rapidsms_httprouter.router import get_router
from rapidsms_httprouter.models import Message
from optparse import make_option
import urlparse
import re
import dateutil

class Command(BaseCommand):


    option_list = BaseCommand.option_list + (
        make_option('-f', '--f', dest='f'),
        )

    def handle(self, **options):
        num=re.compile(r'(\d+)')
        router=get_router()
        file = options['f']
        log=open(file)
        lines=log.readlines()
        for line in lines:

            parts=line.split()
            date=dateutil.parser.parse(parts[0]+" "+parts[1])
            try:
                id_parts=num.split(parts[9])
                id=id_parts[1]
                message=parts[12].rsplit(":")[2][:-1]
                backend=parts[4].split(':')[1][:-1]
                if not Message.objects.filter(direction="I",text=message,connection__identity=id,date__gte=date):

                    router.handle_incoming(backend, id,  message)
                   
            except (IndexError,KeyError):
                pass








