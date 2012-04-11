#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
import traceback
import os
from ureport.settings import UREPORT_ROOT
from django.utils.datastructures import SortedDict
from poll.models import Poll
import datetime
from django.db import connection



class Command(BaseCommand):

    def handle(self, **options):
        try:

            from uganda_common.utils import ExcelResponse

            excel_file_path = \
                os.path.join(os.path.join(os.path.join(UREPORT_ROOT,
                             'static'), 'spreadsheets'),
                             'ureporters.zip')
            export_data_list = []

            # messages=Message.objects.select_related(depth=1)
            # black_listed=Blacklist.objects.values_list('connection__contact__pk',flat=True)
            # print  black_listed
            # black_list_messages=messages.filter(connection__contact__in=black_listed)
            # opt_words=settings.OPT_OUT_WORDS

            year_now = datetime.datetime.now().year
            sql = \
                """    SELECT
      "rapidsms_contact"."id",
      "rapidsms_contact"."name",
      (SELECT
         "rapidsms_connection"."identity"
      FROM
         "rapidsms_connection"
      WHERE
         "rapidsms_connection"."contact_id" = "rapidsms_contact"."id"  LIMIT 1) as identity,
      "rapidsms_contact"."language",
      (SELECT
         DATE("script_scriptsession"."start_time")
      FROM
         "script_scriptsession"
      INNER JOIN
         "rapidsms_connection"
            ON (
               "script_scriptsession"."connection_id" = "rapidsms_connection"."id"
            )
      WHERE
         "rapidsms_connection"."contact_id" = "rapidsms_contact"."id"   LIMIT 1) as autoreg_join_date,
      (SELECT
         DATE("rapidsms_httprouter_message"."date")
      FROM
         "rapidsms_httprouter_message"
      WHERE
         "rapidsms_httprouter_message"."direction" = 'I'
         and "rapidsms_httprouter_message"."application" = 'unregister'
         and  "rapidsms_httprouter_message"."connection_id" = (
            SELECT
               "rapidsms_connection"."id"
            FROM
               "rapidsms_connection"
            WHERE
               "rapidsms_connection"."contact_id" = "rapidsms_contact"."id"  LIMIT 1
         ) LIMIT 1
      ) as quit_date,                                 "locations_location"."name",   (
         %d-EXTRACT('year'
      FROM
         "rapidsms_contact"."birthdate")) as age,

         "rapidsms_contact"."gender",
          "rapidsms_contact"."health_facility" as facility,
         (SELECT
            "locations_location"."name"
         FROM
            "locations_location"
         WHERE
            "locations_location"."id"="rapidsms_contact"."village_id") as village,
         (SELECT
            "auth_group"."name"
         FROM
            "auth_group"
         INNER JOIN
            "rapidsms_contact_groups"
               ON (
                  "auth_group"."id" = "rapidsms_contact_groups"."group_id"
               )
         WHERE
            "rapidsms_contact_groups"."contact_id" = "rapidsms_contact"."id" order by "auth_group"."id" desc  LIMIT 1) as
      group,
      (SELECT
      "rapidsms_httprouter_message"."text"
      FROM "rapidsms_httprouter_message"
        JOIN "poll_response"
            ON "poll_response"."message_id"= "rapidsms_httprouter_message"."id"  where poll_id=121 and contact_id="rapidsms_contact"."id" and has_errors='f' limit 1) as source,
      (SELECT
         COUNT(*) FROM
            "poll_response"
         WHERE
            "poll_response"."contact_id"="rapidsms_contact"."id") as responses,
            (SELECT DISTINCT
         COUNT(*) FROM
            "poll_poll_contacts"
         WHERE
            "poll_poll_contacts"."contact_id"="rapidsms_contact"."id" GROUP BY "poll_poll_contacts"."contact_id") as questions,

            (SELECT DISTINCT count(*)

      FROM "rapidsms_httprouter_message"

   WHERE  "rapidsms_httprouter_message"."direction" ='I'  and

     "rapidsms_httprouter_message"."connection_id" = (
            SELECT
               "rapidsms_connection"."id"
            FROM
               "rapidsms_connection"
            WHERE
               "rapidsms_connection"."contact_id" = "rapidsms_contact"."id"  LIMIT 1
         ) ) as incoming

      FROM
         "rapidsms_contact"
      LEFT JOIN
         "locations_location"
            ON "rapidsms_contact"."reporting_location_id" = "locations_location"."id";
                 """ \
                % year_now
            cursor = connection.cursor()
            cursor.execute(sql)
            row_0 = [(
                'Id',
                'Name',
                'Mobile',
                'Language',
                'Autoreg Join Date',
                'Quit Date',
                'District',
                'Age',
                'Gender',
                'Health Facility',
                'Village',
                'Group',
                'How did you hear about ureport?',
                'Number Of Responses',
                'Number Of Questions Asked',
                'Number of Incoming',
                )]

            rows = row_0 + cursor.fetchall()

            ExcelResponse(rows, output_name=excel_file_path,
                          write_to_file=True)
        except Exception, exc:

            print traceback.format_exc(exc)

        # export the last 2 polls

        polls = Poll.objects.order_by('-pk')
        print "doxing"
        for poll in polls:
            if poll.responses.exists():
                responses = poll.responses.all()
                response_data_list = []
                excel_file_path = \
                    os.path.join(os.path.join(os.path.join(UREPORT_ROOT,
                                 'static'), 'spreadsheets'),
                                 'poll_%d.xls' % poll.pk)
                for response in responses:

                    response_export_data = SortedDict()
                    if response.contact:
                        response_export_data['contact_pk']=response.contact.pk
                    else:
                        response_export_data['contact_pk']=""

                    response_export_data['message_pk']=response.message.pk


                    if response.contact and response.contact.name:
                        response_export_data['contact_name'] = \
                            response.contact.name
                    else:
                        response_export_data['contact_name'] = 'N/A'

                    if response.contact and response.contact.language:
                        response_export_data['language']=response.contact.language
                    else:
                        response_export_data['language']="en"
                           
                    if response.contact and response.contact.gender:
                        response_export_data['sex'] = \
                            response.contact.gender
                    else:
                        response_export_data['sex'] = 'N/A'
                    if response.contact \
                        and response.contact.default_connection:
                        response_export_data['mobile'] = \
                            response.contact.default_connection.identity
                    else:
                        response_export_data['mobile'] = 'N/A'
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
                            response.contact.village.name
                    else:
                        response_export_data['village'] = 'N/A'
                    if response.contact \
                        and response.contact.groups.count() > 0:
                        response_export_data['groups'] = \
                            ','.join([group.name for group in
                                response.contact.groups.all()])
                    else:
                        response_export_data['groups'] = 'N/A'
                    if response.message:
                        response_export_data['response'] = \
                            response.message.text
                        response_export_data['date'] = \
                            response.message.date.date()
                        response_export_data['time'] = \
                            response.message.date.time()
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
                        response_export_data['category'] ="uncategorized"



                    response_data_list.append(response_export_data)
                ExcelResponse(response_data_list,
                              output_name=excel_file_path,
                              write_to_file=True)


