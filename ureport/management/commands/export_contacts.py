from django.core.management.base import BaseCommand
import traceback
import os
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

            excel_file_path = os.path.join(os.path.join(os.path.join(UREPORT_ROOT,'static'),'spreadsheets'),'ureporters.xls')
            contacts = Contact.objects.all()
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

            ExcelResponse(export_data_list,output_name=excel_file_path,write_to_file=True)

        except Exception, exc:
            print traceback.format_exc(exc)
        polls =Poll.objects.all()
        for poll in polls:
            if poll.responses.exists():
                responses=poll.responses.all()
                response_data_list=[]
                excel_file_path = os.path.join(os.path.join(os.path.join(UREPORT_ROOT,'static'),'spreadsheets'),'poll_%d.xls'%poll.pk)
                for response in responses:
                    response_export_data = SortedDict()

                    response_export_data['contact_name'] = response.contact.name
                    if response.contact.gender:
                        response_export_data['sex'] = response.contact.gender
                    else:
                        response_export_data['sex'] = 'N/A'
                    if response.contact.default_connection:
                        response_export_data['mobile']=response.contact.default_connection.identity
                    else:
                        response_export_data['mobile']="N/A"
                    if response.contact.birthdate:
                        try:
                            contact.birthdate.tzinfo = None
                            response_export_data['age'] = (datetime.datetime.now() - response.contact.birthdate).days \
                            / 365
                        except:
                            continue
                    else:
                        response_export_data['age'] = 'N/A'
                    if response.contact.reporting_location:
                        response_export_data['district'] = response.contact.reporting_location.name
                    else:
                        response_export_data['district'] = 'N/A'
                    if response.contact.village:
                        response_export_data['village'] = response.contact.village.name
                    else:
                        response_export_data['village'] = 'N/A'
                    if response.contact.groups.count() > 0:
                        response_export_data['groups'] = ",".join([group.name for group in response.contact.groups.all\
                                ()])
                    else:
                        response_export_data['groups'] = 'N/A'
                    if response.message:
                        response_export_data['response']=response.message.text
                        response_export_data['date']=response.message.date
                    else:
                        response_export_data['response']=''
                        response_export_data['date']=''


                    response_data_list.append(response_export_data)
                ExcelResponse(response_data_list,output_name=excel_file_path,write_to_file=True)

