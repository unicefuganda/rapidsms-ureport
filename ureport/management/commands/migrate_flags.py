from django.core.management.base import BaseCommand
import re
from contact.models import Flag, MessageFlag

class Command(BaseCommand):

    def handle(self, **options):
        fm = MessageFlag.objects.all()
        for message in fm:
            flags = Flag.objects.values_list('name', flat=True).distinct()
            one_template = r"(.*\b(%s)\b.*)"
            w_regex = []
            for word in flags:
                w_regex.append(one_template % str(word).strip())
            reg = re.compile("|".join(w_regex))
            match = reg.search(message.message.text)
            if match:
                message.flag = Flag.objects.get(name=[d for d in list(match.groups()) if d][1])
                message.save()




