from django.core.management import BaseCommand
from rapidsms.models import Contact

__author__ = 'kenneth'

class Command(BaseCommand):

    def handle(self, **options):
        c = Contact.objects.exclude(village=None).update(village=None)