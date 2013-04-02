# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import os
from ureport.settings import UREPORT_ROOT
from django.utils.datastructures import SortedDict
from poll.models import Poll
import datetime
from optparse import make_option

from uganda_common.utils import ExcelResponse
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("-p", "--poll", dest="p"),

    )

    def handle(self, **options):

        poll =Poll.objects.get(pk=int(options['p']))
        
        if poll.responses.exists():
            print 'Working'
            responses = poll.responses.all()
            response_data_list = []
            excel_file_path = \
                os.path.join(os.path.join(os.path.join(UREPORT_ROOT,
                                                       'static'), 'spreadsheets'),
                             'poll_%d.xlsx' % poll.pk)
            for response in responses:

                response_export_data = SortedDict()
                if response.contact:
                    response_export_data['contact_pk'] = response.contact.pk
                else:
                    response_export_data['contact_pk'] = ""

                response_export_data['message_pk'] = response.message.pk

                if response.contact and response.contact.language:
                    response_export_data['language'] = response.contact.language
                else:
                    response_export_data['language'] = "en"

                if response.contact and response.contact.gender:
                    response_export_data['sex'] = \
                        response.contact.gender
                else:
                    response_export_data['sex'] = 'N/A'
                if response.contact and response.contact.birthdate:

                    response_export_data['age'] = \
                        (datetime.datetime.now()
                         - response.contact.birthdate).days / 365
                else:

                    response_export_data['age'] = 'N/A'
                if response.contact \
                    and response.contact.reporting_location:
                    response_export_data['district'] = \
                        response.contact.reporting_location.name
                else:
                    response_export_data['district'] = 'N/A'
                if response.contact and response.contact.village:
                    response_export_data['village'] = \
                        response.contact.village_name
                else:
                    response_export_data['village'] = 'N/A'
                if response.contact and response.contact.subcounty:
                    response_export_data['subcounty'] = \
                        response.contact.subcounty.name
                else:
                    response_export_data['subcounty'] = 'N/A'
                if response.contact \
                    and response.contact.groups.count() > 0:
                    gr = list(response.contact.groups.order_by('pk').values_list('name', flat=True))
                    try:
                        response_export_data['group1'] = gr[0]
                    except IndexError:
                        response_export_data['group1'] = "N/A"
                    try:
                        response_export_data['group2'] = gr[1]
                    except IndexError:
                        response_export_data['group2'] = "N/A"
                    try:
                        response_export_data['group3'] = gr[2]
                    except IndexError:
                        response_export_data['group3'] = "N/A"

                    response_export_data['groups'] = \
                        ','.join([group.name for group in
                                  response.contact.groups.all()])
                else:
                    response_export_data['groups'] = 'N/A'
                    response_export_data['group1'] = response_export_data['group2'] = response_export_data[
                        'group3'] = 'N/A'
                if response.message:
                    response_export_data['response'] = \
                        response.message.text
                    response_export_data['date'] = \
                        response.message.date.strftime("%Y-%m-%d")
                    response_export_data['time'] = \
                        response.message.date.strftime("%H:%M:%S")
                else:

                    response_export_data['response'] = ''
                    response_export_data['date'] = ''
                    response_export_data['time'] = ''
                if response.poll:
                    response_export_data['question'] = \
                        response.poll.question
                else:
                    response_export_data['question'] = ''

                if response.categories.all().exists():
                    response_export_data['category'] = response.categories.all()[0].category.name
                else:
                    response_export_data['category'] = "uncategorized"

                response_data_list.append(response_export_data)
            ExcelResponse(response_data_list,output_name=excel_file_path,write_to_file=True)

