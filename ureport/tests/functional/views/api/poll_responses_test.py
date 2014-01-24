from django.test import TestCase
from rapidsms.models import Backend


class PollResponsesTestCase(TestCase):
    def test_url_for_poll_responses_returns_200(self):
        Backend.objects.create(name="console")
        response = self.client.post("/api/v1/ureporters/console/999/poll/1/responses")
        self.assertEqual(200, response.status_code)

    def test_404_is_thrown_if_backend_does_not_exist(self):
        response = self.client.post("/api/v1/ureporters/console/999/poll/1/responses")
        self.assertEqual(404, response.status_code)
