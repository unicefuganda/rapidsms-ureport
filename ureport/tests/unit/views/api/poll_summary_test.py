import base64
from django.http import Http404
from unittest import TestCase
from django.test import RequestFactory
from mock import Mock
import mock
from poll.models import Poll
from rapidsms.models import Backend, Connection
from ureport.views.api.poll_summary import PollSummary
import json


class PollSummaryTest(TestCase):
    
    def setUp(self):
        self.view = PollSummary()

    def build_kwargs(self, backend_name, user_address, poll_id):
        return {"backend": backend_name, "user_address": user_address, "poll_id": poll_id}

    def get_http_response_from_view(self, kwargs, view):
        request_factory = RequestFactory()
        auth_string = base64.b64encode("who:why")
        fake_request = request_factory.get('/', **{"HTTP_AUTHORIZATION": ("Basic %s" % auth_string)})
        view.validate_credentials = Mock(return_value=True)
        return view.dispatch(fake_request, None, **kwargs)

    def test_404_is_raised_if_backend_does_not_exist(self):
        with self.assertRaises(Http404):
            response = self.get_http_response_from_view(self.build_kwargs("my_backend","77777","12"), self.view)

    def test_404_is_raised_when_no_contact_exists(self):
        self.view.get_backend = Mock(return_value=Backend(name="test"))
        self.view.get_connection = Mock(return_value=None)
        self.view.contact_exists = Mock(return_value=False)
        response = self.get_http_response_from_view( \
                self.build_kwargs("my_backend","77777","12"), self.view)
        data = json.loads(response.content)
        self.assertEquals(404, response.status_code)
        self.assertDictEqual({"success": False, "reason": "Ureporter not found"}, data)

    def test_404_is_raised_when_no_poll_exists(self):
        backend = Backend(name="test")
        self.view.get_connection = Mock(return_value=Connection(identity="77777", backend=backend))
        self.view.get_backend = Mock(return_value=backend)
        self.view.contact_exists = Mock(return_value=True)
        with self.assertRaises(Http404):
            response = self.get_http_response_from_view(self.build_kwargs("my_backend","77777","12"), self.view)


    def test_that_post_returns_405_status_code(self):
        request_factory = RequestFactory()
        fake_request = request_factory.post("/")
        response = self.view.post(fake_request)
        self.assertEqual(405, response.status_code)

    def test_that_gets_poll_summary_if_poll_exists(self):
        poll = mock.Mock(spec=Poll)
        poll.id = 12
        poll.responses = mock.Mock()
        poll.responses.count = Mock(return_value=2)
        fake_summary_responses = [{"name": "Choice 1", "count": 2}, { "name": "Choice 2", "count": 1}]
        self.view.get_responses_summary_for_poll = Mock(return_value=fake_summary_responses)
        self.view.get_total_categorized_responses = Mock(return_value=3)
        data = self.view.get_poll_summary(poll)
        expected_data = {"total_responses": 2,
                         "total_categorized_responses":3,
                          "responses": [
                              {
                                "name": "Choice 1",
                                "count": 2
                              },
                              {
                                "name": "Choice 2",
                                "count": 1
                              }
                          ]
                        }
        self.assertDictEqual(expected_data, data)

    def test_that_get_responses_total_count_returns_the_sum_of_the_responses_summary(self):
        fake_summary_responses = [{"name": "Choice 1", "count": 2}, { "name": "Choice 2", "count": 1}]
        self.assertEquals(3,self.view.get_total_categorized_responses(fake_summary_responses))

    def test_that_valid_get_request_returns_poll_summary(self):
        backend = Backend(name="test")
        self.view.get_connection = Mock(return_value=Connection(identity="77777", backend=backend))
        self.view.get_backend = Mock(return_value=backend)
        self.view.contact_exists = Mock(return_value=True)
        self.view.get_poll = Mock(return_value=Poll(question="Testing?"))
        poll_summary = {"total": 1, "responses": [{"name": "T", "count": 1}]}
        self.view.get_poll_summary = Mock(return_value=poll_summary)
        expected_data = { "success": True, "poll_result": poll_summary }

        response = self.get_http_response_from_view(self.build_kwargs("my_backend","77777","12"), self.view)
        data = json.loads(response.content)

        self.assertEquals(200,response.status_code)
        self.assertDictEqual(expected_data, data)
