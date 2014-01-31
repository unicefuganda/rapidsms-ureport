import datetime
from django.contrib.auth.models import User
from django.test import TestCase
from poll.models import Poll
from rapidsms.models import Contact
from ureport.views.api.poll_topics import PollTopicsApiView


class PollTopicsTest(TestCase):
    def setUp(self):
        self.view = PollTopicsApiView()

    def test_that_only_active_polls_are_returned(self):
        contact, contact_created = Contact.objects.get_or_create(name='John Jonny')
        user, user_created = User.objects.get_or_create(username="test_user")
        an_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
        two_hours_ago = datetime.datetime.now() - datetime.timedelta(hours=2)
        thirty_minutes_ago = datetime.datetime.now() - datetime.timedelta(minutes=30)

        poll, poll_created = Poll.objects.get_or_create(name="Test Poll", question="Is working?", user=user,
                                                        start_date=two_hours_ago)
        second_poll, poll_created = Poll.objects.get_or_create(name="Test Poll 2", question="Is working 2 ?", user=user,
                                                               start_date=an_hour_ago, end_date=thirty_minutes_ago)
        third_poll, poll_created = Poll.objects.get_or_create(name="Test Poll 3", question="Is working 3 ?", user=user)
        poll.contacts = [contact]
        poll.save()

        second_poll.contacts = [contact]
        second_poll.save()

        third_poll.contacts = [contact]
        third_poll.save()
        poll_topics = self.view.get_polls_for_contact(contact)
        self.assertListEqual([{"poll_id": poll.id, "label": "Test Poll"}], poll_topics)

