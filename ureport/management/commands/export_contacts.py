from django.core.management.base import BaseCommand
import traceback
import os
from ureport.settings import UREPORT_ROOT
from rapidsms.models import Contact
from django.utils.datastructures import SortedDict
class Command(BaseCommand):

    def handle(self, **options):
        try:

            from uganda_common.utils import ExcelResponse
            excel_file_path = os.path.join(os.path.join(UREPORT_ROOT,'static'),'ureporters.xls')
            excel_file=open(excel_file_path,'w')

            contacts = Contact.objects.all()[0:100]
            export_data_list = []
            for contact in contacts:
                if contact.name:
                    print "adding " + contact.name
                    export_data = SortedDict()
                    export_data['name'] = contact.name
                    if contact.gender:
                        export_data['sex'] = contact.gender
                    else:
                        export_data['sex'] = 'N/A'
                    if contact.birthdate:
                        try:
                            contact.birthdate.tzinfo = None
                            export_data['age'] = (datetime.datetime.now() - contact.birthdate).days / 365
                        except:
                            continue
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

                    export_data_list.append(export_data)

            response = ExcelResponse(export_data_list,output_name=excel_file_path,write_to_file=True)
            response.write(excel_file)
            excel_file.close()

        except Exception, exc:
            print traceback.format_exc(exc)

