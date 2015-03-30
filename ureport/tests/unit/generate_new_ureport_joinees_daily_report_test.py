import os
import datetime

from django.test import TestCase
from rapidsms_ureport.ureport.tasks import generate_new_ureporters_spreadsheet
from rapidsms_ureport.ureport.tests.factories.connection_factory import ConnectionFactory
from rapidsms_ureport.ureport.tests.factories.contact_factory import ContactFactory
from rapidsms_ureport.ureport.tests.factories.location_factory import LocationFactory
from rapidsms_ureport.ureport.tests.factories.message_factory import MessageFactory
from rapidsms_ureport.ureport.tests.factories.poll_factory import PollFactory
from rapidsms_ureport.ureport.tests.factories.response_factory import ResponseFactory
from settings import filedir
from mock import patch
import settings


class NewUreporterGeneratorTest(TestCase):
    def setUp(self):
        self.contact_one = ContactFactory(reporting_location=(LocationFactory(name="Kampala")),
                                          gender='m', birthdate=datetime.datetime(1990, 1, 1))
        self.connection_one = ConnectionFactory(id=1, contact=self.contact_one)

        self.contact_two = ContactFactory(reporting_location=(LocationFactory(name="Gulu")))
        self.connection_two = ConnectionFactory(id=2, contact=self.contact_two)

        self.contact_three = ContactFactory(reporting_location=(LocationFactory(name="Mukono")),
                                            gender='f', birthdate=datetime.datetime(1998, 10, 1))
        self.connection_three = ConnectionFactory(id=3, contact=self.contact_three)

        channel_response_one = MessageFactory(text='Through radio', connection=self.connection_one)
        channel_response_two = MessageFactory(text='From a friend', connection=self.connection_two)
        channel_response_three = MessageFactory(text='From my MP', connection=self.connection_three)

        poll = PollFactory(name="youthgroup")

        ResponseFactory(poll=poll, message=channel_response_one, contact=self.contact_one)
        ResponseFactory(poll=poll, message=channel_response_two, contact=self.contact_two)
        ResponseFactory(poll=poll, message=channel_response_three, contact=self.contact_three)

        self.today = datetime.datetime.today()
        self.yesterday = self.today - datetime.timedelta(days=1)
        self.UREPORTERS_RELATIVE_FILE_PATH = 'rapidsms_ureport/ureport/static/spreadsheets/' \
                                             'daily-new-ureporters/new-ureporters-%s.xlsx'
        self.UREPORTERS_ABS_FILE_PATH = '/%s' % self.UREPORTERS_RELATIVE_FILE_PATH

    @patch('uganda_common.utils.create_workbook')
    def test_should_generate_new_ureporters_data(self, mock_create_workbook):
        report_file_name = self.UREPORTERS_RELATIVE_FILE_PATH % self.today.date()
        expected_headers = ['date', 'Id', 'District', 'gender', 'date of birth', 'How did you hear about U-report?']

        expected_data = [
            [str(self.contact_one.created_on.date()), self.connection_one.id,
             "Kampala", u'm', '1990-01-01', "Through radio"],
            [str(self.contact_two.created_on.date()), self.connection_two.id, "Gulu", '', '', "From a friend"],
            [str(self.contact_three.created_on.date()), self.connection_three.id,
             "Mukono", u'f', '1998-10-01', "From my MP"]
        ]

        generate_new_ureporters_spreadsheet()

        mock_create_workbook.assert_called_once_with(expected_data, report_file_name, expected_headers)

    def test_should_generate_excel_report_containing_new_ureporters(self):
        report_file_name = filedir + self.UREPORTERS_ABS_FILE_PATH % self.today.date()
        generate_new_ureporters_spreadsheet()
        self.assertTrue(os.path.exists(report_file_name))
        os.remove(report_file_name)

    @patch('django.core.mail.send_mail')
    def test_should_send_new_ureporters_email_notification(self, mock_send_mail):
        date_format = '%b %d, %Y at %H:%m'
        yesterday_str = self.yesterday.strftime(date_format)
        today_str = self.today.strftime(date_format)
        message = '\n    Hello,\n\n    Please find the list of new U-reporters who joined since yesterday %s to ' \
                  'today %s here:\n\n    http://ureport.ug/static/ureport/spreadsheets/daily-new-ureporters/' \
                  'new-ureporters-%s.xlsx\n\n    ' \
                  'Have a nice day,\n    U-report team\n\n    '
        message = message % (yesterday_str, today_str, self.today.date())
        subject = 'Daily Ureporters Joining Details'

        generate_new_ureporters_spreadsheet()

        mock_send_mail.assert_called_once_with(subject, message, settings.DEFAULT_FROM_EMAIL,
                                               settings.PROJECT_MANAGERS, fail_silently=True)

        report_file_name = filedir + self.UREPORTERS_ABS_FILE_PATH % self.today.date()
        os.remove(report_file_name)