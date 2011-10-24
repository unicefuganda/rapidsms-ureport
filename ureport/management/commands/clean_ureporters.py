from django.core.management.base import BaseCommand
import traceback
import os
from script.models import ScriptSession
from ureport.settings import UREPORT_ROOT
from rapidsms.models import Contact
from django.utils.datastructures import SortedDict
from poll.models import Poll
import datetime
import optparse

class Command(BaseCommand):

    def handle(self, **options):
        try:

            from uganda_common.utils import ExcelResponse

            excel_file_path = os.path.join(os.path.join(os.path.join(UREPORT_ROOT, 'static'), 'spreadsheets'), 'ureporters_full.xls')
            contacts = Contact.objects.all()
            export_data_list = []
            for contact in contacts:
                if contact.name:
                    print "adding " + contact.name
                    export_data = SortedDict()
                    export_data['name'] = contact.name
                    if contact.default_connection:
                        export_data['mobile'] = contact.default_connection.identity
                    else:
                        export_data['mobile'] = "N/A"

                    if contact.gender:
                        export_data['sex'] = contact.gender
                    else:
                        export_data['sex'] = 'N/A'
                    if contact.birthdate:

                        #contact.birthdate.tzinfo = None
                        #import pdb;pdb.set_trace()

                        export_data['age'] = (datetime.datetime.now() - contact.birthdate).days / 365

                    else:
                        export_data['age'] = 'N/A'
                    if contact.reporting_location:
                        export_data['district'] = contact.reporting_location.name
                    else:
                        export_data['district'] = 'N/A'
                    if contact.village:
                        export_data['village'] = contact.village.name
                    else:
                        export_data['village'] = 'N/A'
                    if contact.groups.count() > 0:
                        export_data['group'] = contact.groups.all()[0].name
                    else:
                        export_data['group'] = 'N/A'
                    if ScriptSession.objects.filter(connection__contact=contact).exists():
                         export_data["join date"] = ScriptSession.objects.filter(connection__contact=contact)[0].start_time

                    elif contact.default_connection and contact.default_connection.messages.exists():
                        export_data["join date"] = contact.default_connection.messages.order_by('date')[0].date
                    else:
                        export_data["join date"] = "N/A"

                    export_data["Total Poll Responses"] = contact.responses.count()
                    mnum = 0
                    for m in Message.objects.filter(connection__contact=c).order_by('date'):
                        export_data["message %d" % mnum] = m.text
                        export_data["message %d date" % mnum] = str(m.date)
                        mnum += 1
                    export_data_list.append(export_data)

            ExcelResponse(export_data_list, output_name=excel_file_path, write_to_file=True)

        except Exception, exc:
            print traceback.format_exc(exc)
