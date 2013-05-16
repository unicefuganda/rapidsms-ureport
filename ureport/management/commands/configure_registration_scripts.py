from rapidsms_ureport.ureport.utils import configure_messages_for_script

__author__ = 'argha'

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        configure_messages_for_script('ureport_autoreg2',{0:'bar0',1:'bar1', 2:'bar2', 3:'bar3'})