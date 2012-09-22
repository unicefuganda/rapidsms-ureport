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
            date=dateutil.parser.parse(parts[0])
            url=parts[-1].strip()[1:-1]
            url_parts=urlparse.urlparse(url)
            incoming=urlparse.parse_qs(url_parts.query)
            try:
                id_parts=num.split(incoming['sender'][0])
                id=id_parts[1]
                if not Message.objects.filter(direction="I",text=incoming['message'][0],connection__identity=id,date__gte=date):

                    router.handle_incoming(incoming['backend'][0], id,  incoming['message'][0])
                    print incoming
            except (IndexError,KeyError):
                pass








