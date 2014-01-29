import json
import unittest
from django.http import Http404
from django.test import RequestFactory
from django.test.client import FakePayload
from mock import Mock, patch
from poll.models import Poll, Response
from ureport.views.api.poll_responses import SubmitPollResponses


class PollResponsesTest(unittest.TestCase):
    def setUp(self):
        self.view = SubmitPollResponses()

    def test_that_json_data_in_request_is_parsed_correctly_as_json(self):
        message = "Successful message"
        request_factory = RequestFactory()
        fake_request = request_factory.post("/", "{\"message\": \"%s\"}" % message, "application/json")
        data = self.view.get_json_data(fake_request)
        self.assertEqual(message, data['message'])

    def test_that_the_poll_response_is_in_the_correct_format(self):
        request_factory = RequestFactory()
        response = "Yes"
        fake_request = request_factory.post("/", "{\"response\": \"%s\"}" % response, "application/json")
        self.assertEqual(response, self.view.get_incoming_response(fake_request))

    def test_that_in_case_of_get_it_raise_405(self):
        http_response = self.view.get(None)
        self.assertEqual(405, http_response.status_code)

    def test_that_it_raises_a_404_if_the_poll_does_not_exist(self):
        fake_get_poll = Mock(side_effect=Poll.DoesNotExist)
        self.view.get_poll_by_id = fake_get_poll
        with self.assertRaises(Http404):
            self.view.get_poll("23")

    def test_that_if_response_has_errors_accepted_is_false(self):
        fake_poll = Mock()
        fake_poll.process_response = Mock(return_value=(Response(has_errors=True), ""))
        self.view.create_incoming_message = Mock(return_value=None)
        self.view.create_script_response = Mock(return_value=None)
        accepted, message = self.view.process_poll_response("", fake_poll)
        self.assertEqual(accepted, False)

    def test_that_if_response_does_not_have_errors_accepted_is_true(self):
        fake_poll = Mock()
        fake_poll.process_response = Mock(return_value=(Response(has_errors=False), ""))
        self.view.create_incoming_message = Mock(return_value=None)
        self.view.create_script_response = Mock(return_value=None)
        accepted, message = self.view.process_poll_response("", fake_poll)
        self.assertEqual(accepted, True)

    def test_that_if_the_response_has_no_errors_and_the_poll_has_a_script_progress_it_is_moved_on(self):
        fake_poll = Mock()
        fake_progress = Mock()
        fake_moveon_method = Mock()
        fake_progress.moveon = fake_moveon_method
        self.view.get_script_progress_for_poll = Mock(return_value=fake_progress)
        self.view.process_registration_steps(fake_poll)
        assert fake_moveon_method.called

    def test_that_if_the_response_has_no_errors_and_the_poll_has_no_script_progress_it_is_moved_on(self):
        fake_poll = Mock()
        fake_progress = Mock()
        fake_moveon_method = Mock()
        fake_progress.moveon = fake_moveon_method
        self.view.get_script_progress_for_poll = Mock(return_value=None)
        self.view.process_registration_steps(fake_poll)
        assert not fake_moveon_method.called

    def test_that_if_the_response_is_accepted_the_script_steps_are_checked(self):
        self.view.get_poll = Mock(return_value=Poll())
        self.view.get_incoming_response = Mock()
        self.view.process_poll_response = Mock(return_value=(True, ""))
        self.view.create_json_response = Mock()
        fake_process_registration = Mock()
        self.view.process_registration_steps = fake_process_registration
        self.view.post(self, None, **{'poll_id': "12"})
        assert fake_process_registration.called

    def test_that_if_the_response_is_not_accepted_the_script_steps_are_not_checked(self):
        self.view.get_poll = Mock(return_value=Poll())
        self.view.get_incoming_response = Mock()
        self.view.process_poll_response = Mock(return_value=(False, ""))
        self.view.create_json_response = Mock()
        fake_process_registration = Mock()
        self.view.process_registration_steps = fake_process_registration
        self.view.post(self, None, **{'poll_id': "12"})
        assert not fake_process_registration.called

    def test_that_it_returns_a_400_response_if_the_json_is_in_the_wrong_format(self):
        fake_request_factory = RequestFactory()
        fake_request = fake_request_factory.post('/', {"": ""})
        fake_request._raw_post_data = "///sd"
        self.view.get_poll = Mock(return_value=None)
        response = self.view.post(fake_request)
        self.assertEqual(400, response.status_code)

    def test_that_it_returns_a_400_if_the_json_has_no_key_response(self):
        fake_request_factory = RequestFactory()
        fake_request = fake_request_factory.post('/', {"": ""})
        fake_request._raw_post_data = "{}"
        self.view.get_poll = Mock(return_value=None)
        response = self.view.post(fake_request)
        self.assertEqual(400, response.status_code)


