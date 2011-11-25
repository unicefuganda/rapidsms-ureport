from django.core.management.base import BaseCommand
import traceback
import os
from script.models import ScriptSession
from ureport.settings import UREPORT_ROOT
from rapidsms.models import Contact
from django.utils.datastructures import SortedDict
from poll.models import Poll
import datetime
from unregister.models import Blacklist
from django.conf import settings
from rapidsms_httprouter.models import Message
from django.db import connection 


import optparse

class Command(BaseCommand):

    def handle(self, **options):
        try:

            from uganda_common.utils import ExcelResponse

            excel_file_path = os.path.join(os.path.join(os.path.join(UREPORT_ROOT,'static'),'spreadsheets'),'ureporters.xls')
            contacts = Contact.objects.select_related(depth=4)
            export_data_list = []
            messages=Message.objects.select_related(depth=1)
            black_listed=Blacklist.objects.values_list('connection__contact__pk',flat=True)
            print  black_listed
            black_list_messages=messages.filter(connection__contact__in=black_listed)
            opt_words=settings.OPT_OUT_WORDS
            for contact in contacts:
                if contact.name:
                    print "adding " + contact.name
                    export_data = SortedDict()
                    export_data['name'] = contact.name
                    if contact.default_connection:
                        export_data['mobile']=contact.default_connection.identity
                    else:
                        export_data['mobile']="N/A"
                        
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
                         export_data["join date"]=ScriptSession.objects.filter(connection__contact=contact)[0].start_time.date()

                    elif contact.default_connection and contact.default_connection.messages.exists():
                        export_data["join date"]= contact.default_connection.messages.order_by('date')[0].date.date()
                        export_data["join month"]= contact.default_connection.messages.order_by('date')[0].date.month
                    else:
                        export_data["join date"]="N/A"
                        export_data["join month"]="N/A"

                    if contact.pk in black_listed:
                                quit_msg=messages.filter(application="unregister",direction="I",connection__contact=contact).latest('date')
                                export_data['Quit Date']=quit_msg.date.date()
                                export_data['Quit Month']=quit_msg.date.month
                    else:
                        export_data['Quit Date']=''
                        export_data['Quit Month']=''

                    export_data["Total Poll Responses"]=contact.responses.count()

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
                    if response.contact and response.contact.name:
                        response_export_data['contact_name'] = response.contact.name
                    else:
                        response_export_data['contact_name'] = "N/A"
                    if response.contact and response.contact.gender:
                        response_export_data['sex'] = response.contact.gender
                    else:
                        response_export_data['sex'] = 'N/A'
                    if response.contact and response.contact.default_connection:
                        response_export_data['mobile']=response.contact.default_connection.identity
                    else:
                        response_export_data['mobile']="N/A"
                    if response.contact and response.contact.birthdate:

                        response_export_data['age'] = (datetime.datetime.now() - response.contact.birthdate).days/365

                    else:
                        response_export_data['age'] = 'N/A'
                    if response.contact and response.contact.reporting_location:
                        response_export_data['district'] = response.contact.reporting_location.name
                    else:
                        response_export_data['district'] = 'N/A'
                    if response.contact and response.contact.village:
                        response_export_data['village'] = response.contact.village.name
                    else:
                        response_export_data['village'] = 'N/A'
                    if response.contact and response.contact.groups.count() > 0:
                        response_export_data['groups'] = ",".join([group.name for group in response.contact.groups.all\
                                ()])
                    else:
                        response_export_data['groups'] = 'N/A'
                    if response.message:
                        response_export_data['response']=response.message.text
                        response_export_data['date']=response.message.date.date()
                        response_export_data['time']=response.message.date.time

                    else:
                        response_export_data['response']=''
                        response_export_data['date']=''
                        response_export_data['time']=''
                    if response.poll:
                        response_export_data['question']=response.poll.question
                    else:
                        response_export_data['question']=''



                    response_data_list.append(response_export_data)
                ExcelResponse(response_data_list,output_name=excel_file_path,write_to_file=True)

