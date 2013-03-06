from django.core.management import BaseCommand
from poll.models import Poll
from ureport.models import PollAttribute, PollAttributeValue

__author__ = 'kenneth'

class Command(BaseCommand):

    def handle(self, **options):
        PollAttribute.objects.all().delete()
        attr = PollAttribute.objects.create(key='viewable', key_type='bool', default=True)
        for poll in Poll.objects.filter(pk__in=[366, 418, 426, 429, 420]):
            value = PollAttributeValue.objects.create(poll=poll, value=False)
            attr.values.add(value)