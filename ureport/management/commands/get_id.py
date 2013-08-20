from django.core.management import BaseCommand
from django.utils.datastructures import SortedDict
from uganda_common.utils import ExcelResponse
from rapidsms.models import Connection


class Command(BaseCommand):
    def handle(self, *args, **options):
        polls = Connection.objects.all()
        poll_list = []
        for poll in polls:
            print "On Poll ", poll.pk, "===>", poll.identity
            poll_export = SortedDict()
            poll_export['Identity'] = poll.pk
            poll_export['District'] = poll.contact.reporting_location
            poll_export['Phone'] = poll.identity
            poll_export['Gender'] = poll.contact.gender
            poll_list.append(poll_export)
        ExcelResponse(poll_list, output_name='/home/kenneth/all_contacts.xlsx', write_to_file=True)