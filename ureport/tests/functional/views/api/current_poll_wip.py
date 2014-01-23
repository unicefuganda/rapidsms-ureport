
from django.test import TestCase


class CurrentPollTestCase(TestCase):
    def test_url_for_current_poll_returns_200(self):
        response = self.client.get("/ureporters/console/999/polls/current")
        self.assertEqual(200, response.status_code)
