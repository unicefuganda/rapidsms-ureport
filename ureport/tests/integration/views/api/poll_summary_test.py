import datetime
from django.contrib.auth.models import User
from django.test import TestCase
from poll.models import Poll, Category, Response
from rapidsms.models import Backend, Connection, Contact
from rapidsms_httprouter.models import Message
from ureport.views.api.poll_summary import PollSummary


class PollSummaryTest(TestCase):
    def test_that_get_the_response_summary_fo_a_give_poll(self):
        expected_data = [{"name":u"Choice 1", "count":2}, {"name":u"Choice 2", "count":1}]
        data = self.view.get_responses_summary_for_poll(self.poll)
        self.assertListEqual(expected_data, data)

    def setUp(self):
        self.view = PollSummary()
        backend, backend_created = Backend.objects.get_or_create(name="test_backend")
        self.connection, connection_created = Connection.objects.get_or_create(identity="7777", backend=backend)
        self.first_contact, contact_created = Contact.objects.get_or_create(name='John Jonny')
        second_contact, contact_created = Contact.objects.get_or_create(name='Johanna J')
        message, message_created = Message.objects.get_or_create(connection=self.connection, direction="I", text="yes")
        self.user, user_created = User.objects.get_or_create(username="test_user")
        an_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
        self.poll, poll_created = Poll.objects.get_or_create(name="Test Poll", question="Is working?", user=self.user, start_date=an_hour_ago)
        first_category, first_category_created = Category.objects.get_or_create(name="Choice 1", poll=self.poll)
        second_category, second_category_created = Category.objects.get_or_create(name="Choice 2", poll=self.poll)
        first_response = Response.objects.create(message=message, poll=self.poll, contact=self.first_contact)
        second_response = Response.objects.create(message=message, poll=self.poll, contact=second_contact)
        first_response.update_categories([first_category, second_category], self.user)
        second_response.update_categories([first_category], self.user)

    def test_that_response_with_no_category_is_counted(self):
        message, message_created = Message.objects.get_or_create(connection=self.connection, direction="I", text="me")
        response = Response.objects.create(message=message, poll=self.poll, contact=self.first_contact)
        expected_data = [{"name":u"Choice 1", "count":2}, {"name":u"Choice 2", "count":1}, {"name":u"uncategorized", "count":1}]
        data = self.view.get_responses_summary_for_poll(self.poll)
        self.assertListEqual(expected_data, data)