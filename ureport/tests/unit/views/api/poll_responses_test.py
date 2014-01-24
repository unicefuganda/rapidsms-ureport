import unittest
from django.test import RequestFactory
from ureport.views.api.poll_responses import ViewPollResponses


class PollResponsesTest(unittest.TestCase):
    def setUp(self):
        self.view = ViewPollResponses()

    def get_http_response_from_view(self, kwargs, view):
        message = "Successful message"
        request_factory = RequestFactory()
        fake_request = request_factory.post("/", "{\"message\": %s}" % message, "application/json")
        return self.view.post(fake_request, None, **kwargs)

    def test_that_json_data_in_request_is_parsed_correctly_as_json(self):
        message = "Successful message"
        request_factory = RequestFactory()
        fake_request = request_factory.post("/", "{\"message\": \"%s\"}" % message, "application/json")
        data = self.view.get_json_data(fake_request)
        self.assertEqual(message, data['message'])

    def test_that_in_case_of_get_it_raise_405(self):
        http_response = self.view.get(None)
        self.assertEqual(405, http_response.status_code)