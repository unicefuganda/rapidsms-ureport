from unittest import TestCase
from datetime import datetime

from django.test import RequestFactory
from rapidsms_ureport.ureport.models import MessageDetail, MessageAttribute
from rapidsms_ureport.ureport.tests.factories.location_factory import LocationFactory
from rapidsms_ureport.ureport.tests.factories.message_factory import MessageFactory
from rapidsms_ureport.ureport.views.dashboard_views import a_dashboard
from django.contrib.auth.models import User
from contact.models import Flag, MessageFlag
from xlrd import open_workbook


class DashboardViewsTest(TestCase):
    def test_should_all_download_of_all_messages_on_a_dashboard(self):
        request_factory = RequestFactory()
        request = request_factory.get('/dashboard/polio/?download=true')
        request.user = User()
        flag, messages = self.setup_flagged_messages()
        expected_headers = ['message_id', 'Connection ID', 'Message', 'Date',
                            'District', 'Rating', 'Replied', "Forwarded"]

        a_dashboard(request, flag.name)

        sheet = open_workbook('excel_report.xlsx').sheet_by_name('Sheet1')
        header_row = self.extract_row_values_from(sheet, 0)
        self.assertEqual(header_row, expected_headers)

        row_one = self.extract_row_values_from(sheet, 1)
        del row_one[3]  # removes date value because mocking auto date fields on models is messy
        self.assertListEqual(row_one, [float(messages[0].id), float(messages[0].connection.id),
                                       u'message one', u'Kampala', u'5', u'Yes', u'No'])

        row_two = self.extract_row_values_from(sheet, 2)
        del row_two[3]
        self.assertListEqual(row_two, [float(messages[1].id), float(messages[1].connection.id),
                                       u'message two', u'Yumbe', u'', u'No', u'Yes'])

        row_three = self.extract_row_values_from(sheet, 3)
        del row_three[3]
        self.assertListEqual(row_three, [messages[2].id, messages[2].connection.id,
                                         u'message three', u'Mukono', u'', u'No', u'No'])

    def setup_flagged_messages(self):
        polio = Flag.objects.create(name='polio')

        message_one = MessageFactory(text='message one', direction='I', date=datetime(2015, 02, 21))
        message_two = MessageFactory(text='message two', direction='I', date=datetime(2015, 01, 3))
        message_three = MessageFactory(text='message three', direction='I', date=datetime(2014, 01, 3))

        messages = [message_one, message_two, message_three]

        message_one.connection.contact.reporting_location = LocationFactory(name='Kampala')
        message_two.connection.contact.reporting_location = LocationFactory(name='Yumbe')
        message_three.connection.contact.reporting_location = LocationFactory(name='Mukono')

        for message in messages:
            MessageFlag.objects.create(message=message, flag=polio)
            message.connection.contact.save()

        rating = MessageAttribute.objects.create(name='rating')
        replied = MessageAttribute.objects.create(name='replied')
        forwarded = MessageAttribute.objects.create(name='forwarded')

        MessageDetail.objects.create(attribute=rating, message=message_one, value=5)
        MessageDetail.objects.create(attribute=replied, message=message_one)

        MessageDetail.objects.create(attribute=forwarded, message=message_two)

        return polio, messages

    def extract_row_values_from(self, sheet, row_index):
        return [cell.value for cell in sheet.row(row_index)]