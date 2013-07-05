from optparse import make_option
import re
from django.core.management import BaseCommand
from contact.models import Flag, MessageFlag
from rapidsms_httprouter.models import Message


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("-f", "--file", dest="path"),
    )

    def handle(self, **options):
        flag_ = Flag.objects.get(pk=13)
        one_template = r"(.*\b(%s)\b.*)"
        flags = Flag.objects.exclude(rule=None).exclude(rule_regex=None)
        pattern_list = [[re.compile(flag.rule_regex, re.IGNORECASE), flag] for flag in flags if flag.rule]
        for message in Message.objects.filter(pk__in=flag_.messages.values_list('message_id', flat=True)):
            for reg in pattern_list:
                match = reg[0].search(message.text)
                if match:
                    if hasattr(message, 'db_message'):
                        msg = message.db_message
                    else:
                        msg = message
                    mf = MessageFlag.objects.create(message=msg, flag=reg[1])
                    print mf

            #if no rule_regex default to name this is just for backward compatibility ... it will soon die an unnatural death

            flags = Flag.objects.filter(rule=None).values_list('name', flat=True).distinct()

            w_regex = []
            for word in flags:
                w_regex.append(one_template % re.escape(str(word).strip()))
            reg = re.compile(r"|".join(w_regex), re.IGNORECASE)
            match = reg.search(message.text)
            if match:
                #we assume ureport is not the first sms app in the list so there is no need to create db_message
                if hasattr(message, 'db_message'):
                    db_message = message.db_message
                    try:
                        flag = Flag.objects.get(name=[d for d in list(match.groups()) if d][1])
                    except (Flag.DoesNotExist, IndexError):
                        flag = None
                    MessageFlag.objects.create(message=db_message, flag=flag)