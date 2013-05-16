from rapidsms_ureport.ureport.utils import configure_messages_for_script

__author__ = 'argha'

from django.core.management.base import BaseCommand


def parse_line(line,separator='='):
    tokens_list = line.split(separator)
    return  int(tokens_list[0]), tokens_list[1].strip('\n')


class Command(BaseCommand):
    def handle(self, *args, **options):
        file_as_list = list(open("messages.txt"))
        messages_dict = {}
        for line in file_as_list:
            key,value = parse_line(line)
            messages_dict[key] = value
        configure_messages_for_script('ureport_autoreg2', messages_dict)