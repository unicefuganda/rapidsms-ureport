from django.contrib.auth.models import User
from django.test import TestCase
from poll.models import Poll
from rapidsms.models import Backend


class PollResponsesTestCase(TestCase):
    def test_that_url_for_poll_responses_returns_200(self):
        Backend.objects.create(name="console")
        Poll.objects.create(id=1, user=User.objects.create(username="theone"), question="who")
        response = self.client.post("/api/v1/ureporters/console/999/poll/1/responses", {"{\"response\":\"Yes\"}": ""})
        self.assertEqual(200, response.status_code)

    def test_404_is_thrown_if_backend_does_not_exist(self):
        response = self.client.post("/api/v1/ureporters/console/999/poll/1/responses")
        self.assertEqual(404, response.status_code)



