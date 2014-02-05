from django.contrib.auth.models import User
from django.test import TestCase
from poll.models import Poll
from rapidsms.models import Backend, Contact, Connection
from ureport.tests.functional.views.api.helpers import TestBasicAuthMixin


class PollSummaryTest(TestCase, TestBasicAuthMixin):
    def test_that_response_200_when_accessing_poll_summary(self):
        backend,created = Backend.objects.get_or_create(name="console")
        user, user_created = User.objects.get_or_create(username="test_user")
        contact = Contact.objects.create(name="annont")
        connection = Connection.objects.create(backend=backend, identity="999", contact=contact)
        poll = Poll.objects.create(id=12, name="Test Poll", question="Is working?", user=user)
        response = self.client.get("/api/v1/ureporters/console/999/poll/12/summary",**(self.get_auth_headers()))
        self.assertEquals(200, response.status_code)

    def test_that_response_401_when_no_auth_for_poll_summary(self):
        backend,created = Backend.objects.get_or_create(name="console")
        response = self.client.get("/api/v1/ureporters/console/999/poll/12/summary")
        self.assertEquals(401, response.status_code)