import os

from django.test import TestCase
import datetime

from rapidsms_ureport.ureport.tasks import generate_new_ureporters_spreadsheet
from rapidsms_ureport.ureport.tests.factories.connection_factory import ConnectionFactory
from rapidsms_ureport.ureport.tests.factories.contact_factory import ContactFactory
from rapidsms_ureport.ureport.tests.factories.location_factory import LocationFactory
from rapidsms_ureport.ureport.tests.factories.message_factory import MessageFactory
from rapidsms_ureport.ureport.tests.factories.poll_factory import PollFactory
from rapidsms_ureport.ureport.tests.factories.response_factory import ResponseFactory
from settings import filedir
from mock import patch
from rapidsms.models import Connection
import settings


class NewUreporterGeneratorTest(TestCase):
    def setUp(self):
        contact_one = ContactFactory(reporting_location=LocationFactory(name="Kampala"))
        self.ureporter_one = ConnectionFactory(id=1, contact=contact_one)

        contact_two = ContactFactory(reporting_location=LocationFactory(name="Gulu"))
        self.ureporter_two = ConnectionFactory(id=2, contact=contact_two)

        contact_three = ContactFactory(reporting_location=LocationFactory(name="Mukono"))
        self.ureporter_three = ConnectionFactory(id=3, contact=contact_three)

        channel_response_one = MessageFactory(text='Through radio', connection=self.ureporter_one)
        channel_response_two = MessageFactory(text='From a friend', connection=self.ureporter_two)
        channel_response_three = MessageFactory(text='From my MP', connection=self.ureporter_three)

        poll = PollFactory(name="youthgroup")

        ResponseFactory(poll=poll, message=channel_response_one, contact=contact_one)
        ResponseFactory(poll=poll, message=channel_response_two, contact=contact_two)
        ResponseFactory(poll=poll, message=channel_response_three, contact=contact_three)



    @patch('uganda_common.utils.create_workbook')
    def test_generate_new_ureporters_data(self, mock_create_workbook):
        report_file_name = 'rapidsms_ureport/ureport/static/spreadsheets/new-ureporters.xlsx'
        expected_data = [[self.ureporter_one.id, "Kampala", "Through radio"],
                         [self.ureporter_two.id, "Gulu", "From a friend"],
                         [self.ureporter_three.id, "Mukono", "From my MP"]]

        expected_headers = ['Id', 'District', 'How did you hear about U-report?']

        generate_new_ureporters_spreadsheet()

        mock_create_workbook.assert_called_once_with(expected_data, report_file_name, expected_headers)

    def test_generate_excel_report_containing_new_ureporters(self):
        report_file_name = filedir + '/rapidsms_ureport/ureport/static/spreadsheets/new-ureporters.xlsx'
        generate_new_ureporters_spreadsheet()
        self.assertTrue(os.path.exists(report_file_name))
        os.remove(report_file_name)

    @patch('django.core.mail.send_mail')
    def test_generate_new_ureports_sends_email_notification(self, mock_send_mail):
        format = '%b %d, %Y at %H:%m'
        today = datetime.datetime.today()
        yesterday = today - datetime.timedelta(days=1)
        yesterday_str = yesterday.strftime(format)
        today_str = today.strftime(format)
        message ='\n    Hello,\n\n    Please find the list of new U-reporters who joined since yesterday %s to today %s here:\n\n    http://ureport.ug/static/ureport/spreadsheets/new-ureporters.xlsx\n\n    Have a nice day,\n    U-report team\n\n    '
        message = message % (yesterday_str, today_str)
        subject = 'Daily Ureporters Joining Details'

        generate_new_ureporters_spreadsheet()

        mock_send_mail.assert_called_once_with(subject, message, settings.DEFAULT_FROM_EMAIL,
                                  settings.PROJECT_MANAGERS, fail_silently=True)

        report_file_name = filedir + '/rapidsms_ureport/ureport/static/spreadsheets/new-ureporters.xlsx'
        os.remove(report_file_name)