# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from poll.models import Poll
from optparse import make_option

from ureport.utils import export_poll


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("-p", "--poll", dest="p"),

    )

    def handle(self, **options):

        poll =Poll.objects.get(pk=int(options['p']))
        
        export_poll(poll)

