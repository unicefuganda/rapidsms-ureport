import os
from django.core.management import BaseCommand
from datetime import date, datetime
from django.utils.datastructures import SortedDict
from poll.models import Poll
from uganda_common.utils import ExcelResponse
from ureport_project.rapidsms_ureport.ureport.settings import UREPORT_ROOT


class Command(BaseCommand):
    def handle(self, *args, **options):
        excel_file_path = os.path.join(os.path.join(os.path.join(UREPORT_ROOT,
                                               'static'), 'spreadsheets'),
                     'responses.xlsx')
        date_1 = date(2012, 01, 01)
        print date_1
        polls = Poll.objects.filter(start_date__range=[date_1, datetime.now()])
        print polls.count()
        poll_list = []
        for poll in polls:
            print "On Poll ", poll.pk
            resp = poll.responses.count() + 0.0
            cont = poll.contacts.count()
            poll_export = SortedDict()
            poll_export['poll_id'] = poll.pk
            poll_export['poll_name'] = poll.name
            poll_export['question'] = poll.question
            poll_export['Responses'] = resp
            poll_export['Recipients'] = cont
            poll_export['Percentage Response'] = round(resp/cont * 100, 2)
            poll_export['Date'] = str(poll.start_date)
            poll_list.append(poll_export)
        ExcelResponse(poll_list, output_name='/home/kenneth/poll_responses.xlsx', write_to_file=True)